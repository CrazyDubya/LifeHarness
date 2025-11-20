from typing import Dict, Any, List
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.life_entry import LifeEntry
from app.models.user import UserProfile
from app.services.life_entry_service import is_visible
from app.services.llm_orchestrator import llm_orchestrator


async def generate_autobiography(
    db: Session,
    user_id: UUID,
    audience: str,
    date: datetime,
    scope: Dict[str, Any],
    tone: str
) -> Dict[str, Any]:
    """Generate autobiography from visible life entries"""

    # Get profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    # Get all entries
    query = db.query(LifeEntry).filter(LifeEntry.user_id == user_id)

    # Apply scope filters
    if scope.get("type") == "time_range":
        year_from = scope.get("from")
        year_to = scope.get("to")
        if year_from:
            query = query.filter(
                (LifeEntry.approx_year_start >= year_from) |
                (LifeEntry.approx_year_end >= year_from)
            )
        if year_to:
            query = query.filter(
                (LifeEntry.approx_year_start <= year_to) |
                (LifeEntry.approx_year_end <= year_to)
            )

    entries = query.order_by(LifeEntry.approx_year_start).all()

    # Filter by visibility
    visible_entries = [
        entry for entry in entries
        if is_visible(entry, audience, date)
    ]

    # Group by time bucket
    grouped = {}
    for entry in visible_entries:
        bucket = entry.time_bucket
        if bucket not in grouped:
            grouped[bucket] = []
        grouped[bucket].append({
            "headline": entry.headline,
            "distilled": entry.distilled,
            "raw_text": entry.raw_text,
            "timeframe": entry.timeframe_label,
            "topics": entry.topic_buckets,
            "emotional_tone": entry.emotional_tone,
        })

    # Build profile summary
    current_year = datetime.now().year
    user_age = current_year - profile.year_of_birth if profile and profile.year_of_birth else None

    profile_summary = {
        "age": user_age,
        "country": profile.country if profile else None,
        "life_snapshot": profile.life_snapshot if profile else None,
    }

    # Call LLM to synthesize
    result = await llm_orchestrator.generate_autobiography(
        profile_summary=profile_summary,
        grouped_entries=grouped,
        tone=tone,
        audience=audience
    )

    if not result:
        # Fallback
        return {
            "outline": [{"chapter": 1, "title": "My Life", "sections": []}],
            "markdown": "# My Life\n\nAutobiography generation failed."
        }

    return result
