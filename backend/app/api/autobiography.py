from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.autobiography import ViewProfileIn, AutobioOut
from app.services.autobiography_service import generate_autobiography

router = APIRouter()


@router.post("/generate", response_model=AutobioOut)
async def generate_autobiography_endpoint(
    view_profile: ViewProfileIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Generate autobiography for specified audience and scope"""
    result = await generate_autobiography(
        db=db,
        user_id=user.id,
        audience=view_profile.audience,
        date=view_profile.date,
        scope=view_profile.scope,
        tone=view_profile.tone
    )

    return result
