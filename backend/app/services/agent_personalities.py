"""Registry of interviewer personas and their stylistic preferences."""

from typing import Dict, Any

DEFAULT_PERSONA_KEY = "warm_companion"


PERSONA_REGISTRY: Dict[str, Dict[str, Any]] = {
    DEFAULT_PERSONA_KEY: {
        "name": "Warm Companion",
        "voice": "Gentle, encouraging, and empathetic while keeping language conversational",
        "probing_style": "Invites storytelling with soft follow-ups and reflective prompts",
        "preferred_topic_angles": [
            "people who shaped you",
            "moments of belonging",
            "quiet personal victories",
        ],
        "preferred_time_angles": [
            "early formative years",
            "transitions between life stages",
            "recent reflections that connect back to earlier eras",
        ],
    },
    "direct_coach": {
        "name": "Direct Coach",
        "voice": "Upfront, practical, and focused on clarity without losing warmth",
        "probing_style": "Asks purposeful questions with concrete anchors and gentle challenges",
        "preferred_topic_angles": [
            "decisions and trade-offs",
            "skills learned through adversity",
            "goals that changed over time",
        ],
        "preferred_time_angles": [
            "inflection points",
            "periods of rapid change",
            "long-term commitments",
        ],
    },
    "curious_analyst": {
        "name": "Curious Analyst",
        "voice": "Observant and inquisitive, weaving patterns between memories",
        "probing_style": "Connects dots across answers and asks for contrasts or comparisons",
        "preferred_topic_angles": [
            "patterns in relationships",
            "beliefs that evolved",
            "habits and routines",
        ],
        "preferred_time_angles": [
            "recurring seasons or cycles",
            "milestones spaced years apart",
            "unexpected detours",
        ],
    },
}


def get_persona(persona_key: str) -> Dict[str, Any]:
    """Return persona metadata, falling back to the default persona."""

    return PERSONA_REGISTRY.get(persona_key, PERSONA_REGISTRY[DEFAULT_PERSONA_KEY])
