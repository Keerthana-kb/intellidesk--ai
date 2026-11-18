
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.team import Team


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    team_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        default="medium",
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="open",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    organization: Mapped["Organization"] = relationship()
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    assignee: Mapped["User | None"] = relationship(foreign_keys=[assigned_to])
    team: Mapped["Team | None"] = relationship()

    
