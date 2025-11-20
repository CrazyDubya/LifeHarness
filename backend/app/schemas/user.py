from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models.enums import RelationshipStatus, MainRole, IntensityLevel


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserOut(BaseModel):
    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileIn(BaseModel):
    year_of_birth: Optional[int] = None
    country: Optional[str] = None
    primary_language: Optional[str] = None
    relationship_status: Optional[RelationshipStatus] = None
    has_children: Optional[bool] = None
    children_count: Optional[int] = None
    children_age_brackets: Optional[List[str]] = None
    main_role: Optional[MainRole] = None
    field_or_industry: Optional[str] = None
    avoid_topics: Optional[List[str]] = None
    intensity: Optional[IntensityLevel] = IntensityLevel.BALANCED
    life_snapshot: Optional[str] = None


class ProfileOut(BaseModel):
    user_id: UUID
    year_of_birth: Optional[int]
    country: Optional[str]
    primary_language: Optional[str]
    relationship_status: Optional[str]
    has_children: Optional[bool]
    children_count: Optional[int]
    children_age_brackets: Optional[List[str]]
    main_role: Optional[str]
    field_or_industry: Optional[str]
    avoid_topics: Optional[List[str]]
    intensity: Optional[str]
    life_snapshot: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
