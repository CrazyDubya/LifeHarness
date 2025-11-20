from typing import Dict, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.coverage import CoverageGrid


def get_coverage_slice(
    db: Session,
    user_id: UUID,
    time_buckets: List[str],
    topic_buckets: List[str]
) -> Dict[str, Dict[str, int]]:
    """Get coverage scores for specified time and topic buckets"""
    coverage = db.query(CoverageGrid).filter(
        CoverageGrid.user_id == user_id,
        CoverageGrid.time_bucket.in_(time_buckets),
        CoverageGrid.topic_bucket.in_(topic_buckets)
    ).all()

    result = {}
    for time_b in time_buckets:
        result[time_b] = {}
        for topic_b in topic_buckets:
            result[time_b][topic_b] = 0

    for cov in coverage:
        if cov.time_bucket in result:
            result[cov.time_bucket][cov.topic_bucket] = cov.score

    return result


def update_coverage(
    db: Session,
    user_id: UUID,
    time_bucket: str,
    topic_buckets: List[str],
    score_increment: int = 10
):
    """Update coverage scores for a new life entry"""
    for topic_bucket in topic_buckets:
        # Try to get existing
        existing = db.query(CoverageGrid).filter(
            CoverageGrid.user_id == user_id,
            CoverageGrid.time_bucket == time_bucket,
            CoverageGrid.topic_bucket == topic_bucket
        ).first()

        if existing:
            existing.score = min(existing.score + score_increment, 100)
        else:
            new_cov = CoverageGrid(
                user_id=user_id,
                time_bucket=time_bucket,
                topic_bucket=topic_bucket,
                score=score_increment
            )
            db.add(new_cov)

    db.commit()
