import json
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings


class LLMOrchestrator:
    def __init__(self):
        self.api_key = settings.VULTR_API_KEY
        self.base_url = settings.VULTR_API_BASE_URL
        self.model = settings.VULTR_MODEL

    async def _call_api(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """Call Vultr Inference API (OpenAI-compatible)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"LLM API error: {e}")
                return None

    async def generate_question(
        self,
        thread_root: str,
        profile_summary: Dict[str, Any],
        thread_freeforms: List[Dict[str, Any]],
        recent_qa: List[Dict[str, str]],
        coverage_slice: Dict[str, Dict[str, int]],
        allowed_time_buckets: List[str],
        allowed_topic_buckets: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Generate next question for the thread"""

        system_prompt = """You are an ongoing autobiographical interviewer.
Your job is to propose exactly one next question for this thread.

Constraints:
- Stay within this thread's theme, unless gently bridging to a closely related under-explored area.
- Respect the user's age, life stage, and avoid list.
- Do NOT ask about children if they have none and did not create a children-focused thread.
- Prefer concrete, specific questions tied to periods, people, or places.
- Default to multiple-choice with an "Other (I'll explain)" option when possible.
- Focus on areas with low coverage scores to ensure comprehensive life documentation.

Return your response as valid JSON with this structure:
{
  "question": {
    "type": "multiple_choice" or "short_answer",
    "time_focus": ["20s"],
    "topic_focus": ["friendships"],
    "text": "Your question here",
    "options": [
      {"id": "A", "text": "Option A"},
      {"id": "B", "text": "Option B"},
      {"id": "C", "text": "Option C"},
      {"id": "D", "text": "Option D"},
      {"id": "OTHER", "text": "None of these fit (I'll explain)."}
    ]
  }
}

For short_answer questions, omit the "options" field."""

        user_content = json.dumps({
            "thread_root": thread_root,
            "profile": profile_summary,
            "thread_freeforms": thread_freeforms,
            "recent_qa": recent_qa,
            "coverage_slice": coverage_slice,
            "allowed_time_buckets": allowed_time_buckets,
            "allowed_topic_buckets": allowed_topic_buckets
        })

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]

        response = await self._call_api(messages, temperature=0.8, max_tokens=1000)
        if response:
            try:
                # Try to extract JSON from response
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                print(f"Failed to parse LLM response: {response}")
        return None

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
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                print(f"Failed to parse distillation response: {response}")
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

        response = await self._call_api(messages, temperature=0.7, max_tokens=4000)
        if response:
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                print(f"Failed to parse autobiography response: {response}")
        return None


# Singleton instance
llm_orchestrator = LLMOrchestrator()
