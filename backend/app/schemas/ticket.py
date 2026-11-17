
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TicketCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10)
    category: Optional[str] = None
    priority: str = "medium"


class TicketResponse(BaseModel):
    id: str
    title: str
    description: str
    category: Optional[str] = None
    priority: str
    status: str
    created_at: datetime


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
