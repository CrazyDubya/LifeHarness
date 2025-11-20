from typing import Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.life_entry import LifeEntry
from app.models.question import Answer, Question
from app.models.user import UserProfile
from app.services.llm_orchestrator import llm_orchestrator
from app.services.coverage_service import update_coverage
from app.models.enums import VisibilityLevel, SealType


async def create_life_entry_from_freeform(
    db: Session,
    user_id: UUID,
    raw_text: str,
    thread_id: Optional[UUID] = None,
    question_id: Optional[UUID] = None,
    visibility: str = VisibilityLevel.SELF.value,
    seal_type: str = SealType.NONE.value
) -> Optional[LifeEntry]:
    """Create a LifeEntry from freeform text using LLM distillation"""

    # Get user profile for age context
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    current_year = datetime.now().year
    user_age = current_year - profile.year_of_birth if profile and profile.year_of_birth else None

    # Distill using LLM
    distilled_data = await llm_orchestrator.distill_freeform(raw_text, user_age)

    if not distilled_data:
        return None

    # Infer timeframe label
    time_bucket = distilled_data.get("time_bucket", "20s")
    year_start = distilled_data.get("approx_year_start")
    year_end = distilled_data.get("approx_year_end")

    timeframe_label = f"{time_bucket}"
    if year_start:
        if year_end and year_end != year_start:
            timeframe_label = f"{year_start}-{year_end}"
        else:
            timeframe_label = f"{year_start}"

    # Create entry
    entry = LifeEntry(
        user_id=user_id,
        thread_id=thread_id,
        source_question_id=question_id,
        time_bucket=time_bucket,
        approx_year_start=year_start,
        approx_year_end=year_end,
        timeframe_label=timeframe_label,
        headline=distilled_data.get("headline", "Untitled Memory"),
        raw_text=raw_text,
        distilled=distilled_data.get("distilled", raw_text[:500]),
        tags=distilled_data.get("tags", []),
        topic_buckets=distilled_data.get("topic_buckets", []),
        visibility=visibility,
        seal_type=seal_type,
        emotional_tone=distilled_data.get("emotional_tone"),
        people=distilled_data.get("people", []),
        locations=distilled_data.get("locations", []),
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Update coverage
    if entry.topic_buckets:
        update_coverage(db, user_id, time_bucket, entry.topic_buckets)

    return entry


def is_visible(
    entry: LifeEntry,
    audience: str,
    current_date: datetime
) -> bool:
    """Check if an entry is visible to a given audience at a given date"""

    # Hierarchy: self > trusted > heirs > public
    visibility_hierarchy = {
        "self": 0,
        "trusted": 1,
        "heirs": 2,
        "public": 3
    }

    entry_vis_level = visibility_hierarchy.get(entry.visibility, 0)
    audience_level = visibility_hierarchy.get(audience, 3)

    # Entry must be at or above audience level
    if entry_vis_level > audience_level:
        return False

    # Check seal
    if entry.seal_type == SealType.NONE.value:
        return True

    if entry.seal_type == SealType.UNTIL_DATE.value:
        if entry.seal_release_at and current_date < entry.seal_release_at:
            # Check if audience is blocked
            if audience in (entry.seal_audiences_blocked or []):
                return False
        return True

    if entry.seal_type == SealType.UNTIL_EVENT.value:
        # For now, assume event hasn't occurred (would need event tracking system)
        if audience in (entry.seal_audiences_blocked or []):
            return False
        return True

    if entry.seal_type == SealType.UNTIL_MANUAL.value:
        if audience in (entry.seal_audiences_blocked or []):
            return False
        return True

    return True
