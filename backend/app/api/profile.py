from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User, UserProfile
from app.schemas.user import ProfileIn, ProfileOut

router = APIRouter()


@router.post("", response_model=ProfileOut)
def upsert_profile(
    profile_data: ProfileIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Create or update user profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    if profile:
        # Update existing
        for field, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)
    else:
        # Create new
        profile = UserProfile(
            user_id=user.id,
            **profile_data.dict(exclude_unset=True)
        )
        db.add(profile)

    db.commit()
    db.refresh(profile)

    return profile


@router.get("", response_model=ProfileOut)
def get_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user profile"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return profile
