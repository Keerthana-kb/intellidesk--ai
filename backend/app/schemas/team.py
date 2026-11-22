from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TeamCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = Field(
        default=None,
        max_length=255
    )


class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime


class TeamMemberCreate(BaseModel):
    user_id: str


class TeamMemberResponse(BaseModel):
    id: str
    team_id: str
    user_id: str
    user_name: str
    email: str
    joined_at: datetime