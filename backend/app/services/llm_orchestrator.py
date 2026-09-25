import json
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings


# Candidate generation moves. Jev ranks concrete candidates; these moves are
# generation directives and stored tags, not Jev's choice set.
MOVES = ["go_deeper", "pivot_to_gap", "bridge", "freeform_reflection"]

BROWSER_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


class LLMOrchestrator:
    """LLM access via Token Broker (OpenAI-compatible cheap inference).

    The LLM is the writer, not the strategist: it generates batches of tagged
    candidate questions; Jev (via jev_decider) ranks the candidate pool.
    """

    def __init__(self):
        self.api_key = settings.TOKENBROKER_API_KEY
        self.base_url = settings.TOKENBROKER_API_BASE_URL.rstrip("/")
        self.model = settings.TOKENBROKER_MODEL

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": BROWSER_UA,
        }

    async def _call_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        timeout: float = 20.0,
    ) -> Optional[str]:
        """Call the chat-completions endpoint. Short timeout: never hang the
        interview loop the way the old 60s provider call did."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                    timeout=timeout,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"LLM API error: {e}")
                return None

    @staticmethod
    def _extract_json(response: str) -> Optional[Dict[str, Any]]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
        except json.JSONDecodeError:
            print(f"Failed to parse LLM response: {response[:500]}")
        return None

    async def generate_candidates(
        self,
        thread_root: str,
        profile_summary: Dict[str, Any],
        recent_qa: List[Dict[str, str]],
        coverage_gaps: List[Dict[str, Any]],
        allowed_time_buckets: List[str],
        allowed_topic_buckets: List[str],
        persona: Dict[str, Any],
        count: int = 4,
    ) -> List[Dict[str, Any]]:
        """Generate a batch of diverse, tagged candidate questions.

        Candidates are spread across moves (go_deeper / pivot_to_gap / bridge /
        freeform_reflection) and tagged in the same JSON (move, type,
        time_focus, topic_focus) so no separate classifier pass is needed.
        Returns a list of candidate dicts; empty list on failure.
        """
        moves = ", ".join(MOVES)
        system_prompt = f"""You are an autobiographical interviewer embodying the {persona['name']} persona.
Speak with this voice: {persona['voice']}.
Use this probing style: {persona['probing_style']}.

Your job is to propose exactly {count} candidate next questions for this interview thread,
deliberately spread across these moves: {moves}.
- go_deeper: follow up on the last answer while it is warm.
- pivot_to_gap: jump to an uncovered time/topic area from coverage_gaps.
- bridge: connect something the user just said to adjacent uncovered territory.
- freeform_reflection: an open-ended writing prompt (short_answer, no options).

Constraints:
- Respect the user's age, life stage, and avoid list.
- Do NOT ask about children if they have none and did not create a children-focused thread.
- Prefer concrete, specific questions tied to periods, people, or places.
- Default to multiple-choice with an "Other (I'll explain)" option when possible.
- Do NOT repeat or closely paraphrase recent questions.

Return ONLY valid JSON with this structure:
{{
  "candidates": [
    {{
      "move": "go_deeper",
      "type": "multiple_choice",
      "time_focus": ["20s"],
      "topic_focus": ["friendships"],
      "text": "Your question here",
      "options": [
        {{"id": "A", "text": "Option A"}},
        {{"id": "B", "text": "Option B"}},
        {{"id": "C", "text": "Option C"}},
        {{"id": "OTHER", "text": "None of these fit (I'll explain)."}}
      ]
    }},
    {{
      "move": "freeform_reflection",
      "type": "short_answer",
      "time_focus": ["10s"],
      "topic_focus": ["creativity_play"],
      "text": "Your open prompt here"
    }}
  ]
}}

time_focus values must come from: {allowed_time_buckets}.
topic_focus values must come from: {allowed_topic_buckets}.
For short_answer candidates, omit the "options" field."""

        user_content = json.dumps({
            "thread_root": thread_root,
            "profile": profile_summary,
            "recent_qa": recent_qa,
            "coverage_gaps": coverage_gaps,
            "persona": persona,
        })

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

        response = await self._call_api(messages, temperature=0.8, max_tokens=1800)
        if not response:
            return []
        data = self._extract_json(response)
        if not data or "candidates" not in data:
            return []

        valid = []
        for c in data["candidates"]:
            if not isinstance(c, dict) or "text" not in c:
                continue
            if c.get("move") not in MOVES:
                c["move"] = "pivot_to_gap"
            if c.get("type") not in ("multiple_choice", "short_answer"):
                c["type"] = "multiple_choice" if c.get("options") else "short_answer"
            valid.append({
                "move": c["move"],
                "type": c["type"],
                "text": c["text"],
                "options": c.get("options"),
                "time_focus": c.get("time_focus", []),
                "topic_focus": c.get("topic_focus", []),
            })
        return valid

    async def distill_freeform(
        self,
        raw_text: str,
        user_age: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Distill freeform answer into structured LifeEntry data"""

        system_prompt = """Summarize this memory, infer its approximate time in life and main topics.

Return JSON with this structure:
{
  "headline": "Brief headline of this memory",
  "distilled": "Concise summary in 2-3 sentences",
  "time_bucket": "20s" (one of: pre10, 10s, 20s, 30s, 40s, 50plus),
  "approx_year_start": 2007,
  "approx_year_end": 2009,
  "topic_buckets": ["work_career", "crises_turning_points"],
  "tags": ["NYC", "startup", "burnout"],
  "emotional_tone": "anxious but hopeful",
  "people": ["boss", "partner"],
  "locations": ["New York"]
}

Topic buckets must be from: family_of_origin, friendships, romantic_love, children,
work_career, money_status, health_body, creativity_play, beliefs_values, crises_turning_points"""

        user_content = f"User's memory:\n\n{raw_text}"
        if user_age:
            user_content += f"\n\nUser's current age: {user_age}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = await self._call_api(messages, temperature=0.5, max_tokens=800)
        if response:
            return self._extract_json(response)
        return None

    async def generate_autobiography(
        self,
        profile_summary: Dict[str, Any],
        grouped_entries: List[Dict[str, Any]],
        tone: str,
        audience: str
    ) -> Optional[Dict[str, Any]]:
        """Generate autobiography from life entries"""

        system_prompt = f"""You are a skilled autobiographer. Generate a comprehensive autobiography
based on the provided life entries.

Audience: {audience}
Tone: {tone}

Return JSON with this structure:
{{
  "outline": [
    {{"chapter": 1, "title": "Early Years", "sections": ["Childhood", "School days"]}},
    {{"chapter": 2, "title": "Coming of Age", "sections": [...]}},
    ...
  ],
  "markdown": "# Chapter 1: Early Years\\n\\n## Childhood\\n\\n..."
}}

Make the narrative compelling, coherent, and true to the person's voice.
Use markdown formatting for structure."""

        user_content = json.dumps({
            "profile": profile_summary,
            "entries": grouped_entries,
            "tone": tone,
            "audience": audience
        })

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = await self._call_api(messages, temperature=0.7, max_tokens=4000,
                                        timeout=60.0)
        if response:
            return self._extract_json(response)
        return None


# Singleton instance
llm_orchestrator = LLMOrchestrator()
