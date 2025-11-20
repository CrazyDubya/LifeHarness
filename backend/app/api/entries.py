from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.life_entry import LifeEntry
from app.models.coverage import CoverageGrid
from app.schemas.life_entry import LifeEntryOut, SealUpdateIn, CoverageGridOut

router = APIRouter()


@router.get("", response_model=List[LifeEntryOut])
def list_entries(
    time_bucket: Optional[str] = Query(None),
    topic_bucket: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List user's life entries with optional filters"""
    query = db.query(LifeEntry).filter(LifeEntry.user_id == user.id)

    if time_bucket:
        query = query.filter(LifeEntry.time_bucket == time_bucket)

    if topic_bucket:
        query = query.filter(LifeEntry.topic_buckets.contains([topic_bucket]))

    entries = query.order_by(LifeEntry.approx_year_start).all()

    return entries


@router.get("/{entry_id}", response_model=LifeEntryOut)
def get_entry(
    entry_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a specific life entry"""
    entry = db.query(LifeEntry).filter(
        LifeEntry.id == entry_id,
        LifeEntry.user_id == user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    return entry


@router.patch("/{entry_id}/seal", response_model=LifeEntryOut)
def update_seal(
    entry_id: UUID,
    seal_data: SealUpdateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update seal settings for an entry"""
    entry = db.query(LifeEntry).filter(
        LifeEntry.id == entry_id,
        LifeEntry.user_id == user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Update fields
    for field, value in seal_data.dict(exclude_unset=True).items():
        setattr(entry, field, value)

    db.commit()
    db.refresh(entry)

    return entry


@router.get("/coverage/grid", response_model=List[CoverageGridOut])
def get_coverage_grid(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get coverage grid for heatmap visualization"""
    coverage = db.query(CoverageGrid).filter(
        CoverageGrid.user_id == user.id
    ).all()

    return coverage
