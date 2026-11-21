
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

# =====================================
# TICKET COMMENT SCHEMAS
# =====================================

class TicketCommentCreate(BaseModel):
    comment: str = Field(min_length=1, max_length=5000)



class TicketCommentResponse(BaseModel):
    id: str
    ticket_id: str
    user_id: str
    user_name: str
    comment: str
    created_at: datetime

class TicketAssign(BaseModel):
    assigned_to: str


class TicketEventResponse(BaseModel):
    id: str
    ticket_id: str
    user_id: Optional[str] = None
    event_type: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime
    user_name: Optional[str] = None


