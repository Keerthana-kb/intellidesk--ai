
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.ticket import TicketAssign
import uuid
from app.models.ticket_event import TicketEvent
from app.schemas.ticket import TicketEventResponse

from app.db.session import get_db
from app.models.ticket import Ticket
from app.models.ticket_comment import TicketComment
from app.models.user import User

from app.schemas.ticket import (
    TicketCreate,
    TicketResponse,
    TicketUpdate,
    TicketCommentCreate,
    TicketCommentResponse
)

from app.api.deps import get_current_user, require_roles

router = APIRouter()


# =====================================
# CREATE TICKET API
# =====================================


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED
)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_ticket = Ticket(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        title=ticket_data.title,
        description=ticket_data.description,
        category=ticket_data.category,
        priority=ticket_data.priority,
        status="open"
    )

    db.add(new_ticket)
    db.flush()

    new_event = TicketEvent(
        ticket_id=new_ticket.id,
        user_id=current_user.id,
        event_type="ticket_created",
        old_value=None,
        new_value="open"
    )

    db.add(new_event)

    db.commit()
    db.refresh(new_ticket)

    return TicketResponse(
        id=str(new_ticket.id),
        title=new_ticket.title,
        description=new_ticket.description,
        category=new_ticket.category,
        priority=new_ticket.priority,
        status=new_ticket.status,
        created_at=new_ticket.created_at
    )


# =====================================
# VIEW MY TICKETS API
# =====================================

@router.get(
    "/my-tickets",
    response_model=list[TicketResponse]
)
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tickets = db.query(Ticket).filter(
        Ticket.created_by == current_user.id,
        Ticket.organization_id == current_user.organization_id
    ).order_by(
        Ticket.created_at.desc()
    ).all()

    return [
        TicketResponse(
            id=str(ticket.id),
            title=ticket.title,
            description=ticket.description,
            category=ticket.category,
            priority=ticket.priority,
            status=ticket.status,
            created_at=ticket.created_at
        )
        for ticket in tickets
    ]


# =====================================
# VIEW ALL TICKETS API
# =====================================

@router.get(
    "/",
    response_model=list[TicketResponse]
)
def get_all_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "support_engineer")
    )
):
    tickets = db.query(Ticket).filter(
        Ticket.organization_id == current_user.organization_id
    ).order_by(
        Ticket.created_at.desc()
    ).all()

    return [
        TicketResponse(
            id=str(ticket.id),
            title=ticket.title,
            description=ticket.description,
            category=ticket.category,
            priority=ticket.priority,
            status=ticket.status,
            created_at=ticket.created_at
        )
        for ticket in tickets
    ]


# =====================================
# UPDATE TICKET STATUS API
# =====================================


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse
)
def update_ticket_status(
    ticket_id: str,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "support_engineer")
    )
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user.organization_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    if ticket_data.status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status is required"
        )

    allowed_statuses = [
        "open",
        "in_progress",
        "resolved",
        "closed"
    ]

    if ticket_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket status"
        )

    # Store previous status
    old_status = ticket.status

    # Update status
    ticket.status = ticket_data.status

    # Record event only if status actually changes
    if old_status != ticket_data.status:
        new_event = TicketEvent(
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type="status_changed",
            old_value=old_status,
            new_value=ticket_data.status
        )

        db.add(new_event)

    db.commit()
    db.refresh(ticket)

    return TicketResponse(
        id=str(ticket.id),
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        created_at=ticket.created_at
    )


# =====================================
# UPDATE TICKET PRIORITY API
# =====================================

@router.patch(
    "/{ticket_id}/priority",
    response_model=TicketResponse
)
def update_ticket_priority(
    ticket_id: str,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "support_engineer")
    )
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user.organization_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    if ticket_data.priority is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Priority is required"
        )

    allowed_priorities = [
        "low",
        "medium",
        "high",
        "critical"
    ]

    if ticket_data.priority not in allowed_priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket priority"
        )

    # Store previous priority
    old_priority = ticket.priority

    # Update priority
    ticket.priority = ticket_data.priority

    # Record event only if priority changes
    if old_priority != ticket_data.priority:
        new_event = TicketEvent(
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type="priority_changed",
            old_value=old_priority,
            new_value=ticket_data.priority
        )

        db.add(new_event)

    db.commit()
    db.refresh(ticket)

    return TicketResponse(
        id=str(ticket.id),
        title=ticket.title,
        description=ticket.description,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        created_at=ticket.created_at
    )


# =====================================
# DELETE TICKET API
# =====================================

@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin")
    )
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user.organization_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    db.delete(ticket)
    db.commit()

    return {
        "message": "Ticket deleted successfully",
        "ticket_id": ticket_id
    }


# =====================================
# ADD TICKET COMMENT API
# =====================================

@router.post(
    "/{ticket_id}/comments",
    response_model=TicketCommentResponse,
    status_code=status.HTTP_201_CREATED
)
def add_ticket_comment(
    ticket_id: str,
    comment_data: TicketCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user.organization_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    new_comment = TicketComment(
        ticket_id=ticket.id,
        user_id=current_user.id,
        comment=comment_data.comment
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return TicketCommentResponse(
        id=str(new_comment.id),
        ticket_id=str(new_comment.ticket_id),
        user_id=str(new_comment.user_id),
        user_name=current_user.full_name,
        comment=new_comment.comment,
        created_at=new_comment.created_at
    )


# =====================================
# VIEW TICKET COMMENTS API
# =====================================

@router.get(
    "/{ticket_id}/comments",
    response_model=list[TicketCommentResponse]
)
def get_ticket_comments(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user.organization_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    comments = db.query(
        TicketComment,
        User.full_name
    ).join(
        User,
        TicketComment.user_id == User.id
    ).filter(
        TicketComment.ticket_id == ticket.id
    ).order_by(
        TicketComment.created_at.asc()
    ).all()

    return [
        TicketCommentResponse(
            id=str(comment.id),
            ticket_id=str(comment.ticket_id),
            user_id=str(comment.user_id),
            user_name=user_name,
            comment=comment.comment,
            created_at=comment.created_at
        )
        for comment, user_name in comments
    ]


@router.patch("/{ticket_id}/assign")
def assign_ticket(
    ticket_id: str,
    assignment: TicketAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("admin", "support_engineer")
    )
):
    # Find the ticket
    ticket = db.query(Ticket).filter(
        Ticket.id == uuid.UUID(ticket_id),
        Ticket.organization_id == current_user.organization_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Validate assigned user ID
    try:
        assigned_user_id = uuid.UUID(assignment.assigned_to)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid user ID"
        )

    # Find support engineer in the same organization
    support_engineer = db.query(User).filter(
        User.id == assigned_user_id,
        User.organization_id == current_user.organization_id,
        User.role == "support_engineer",
        User.is_active == True
    ).first()

    if not support_engineer:
        raise HTTPException(
            status_code=404,
            detail="Active support engineer not found"
        )

    # Store previous assigned user
    old_assigned_to = ticket.assigned_to

    # Assign ticket
    ticket.assigned_to = support_engineer.id

    # Record assignment event only if assignment changes
    if old_assigned_to != support_engineer.id:
        new_event = TicketEvent(
            ticket_id=ticket.id,
            user_id=current_user.id,
            event_type="ticket_assigned",
            old_value=str(old_assigned_to) if old_assigned_to else None,
            new_value=str(support_engineer.id)
        )

        db.add(new_event)

    db.commit()
    db.refresh(ticket)

    return {
        "message": "Ticket assigned successfully",
        "ticket_id": str(ticket.id),
        "assigned_to": str(support_engineer.id),
        "assigned_user_name": support_engineer.full_name
    }


@router.get("/assigned-to-me", response_model=list[TicketResponse])
def get_assigned_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("support_engineer"))
):
    tickets = db.query(Ticket).filter(
        Ticket.assigned_to == current_user.id,
        Ticket.organization_id == current_user.organization_id
    ).order_by(
        Ticket.created_at.desc()
    ).all()

    return [
        TicketResponse(
            id=str(ticket.id),
            title=ticket.title,
            description=ticket.description,
            category=ticket.category,
            priority=ticket.priority,
            status=ticket.status,
            created_at=ticket.created_at
        )
        for ticket in tickets
    ]


@router.get("/{ticket_id}/events", response_model=list[TicketEventResponse])
def get_ticket_events(
    ticket_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Find ticket within the user's organization
    try:
        ticket_uuid = uuid.UUID(ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticket ID"
        )

    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_uuid,
        Ticket.organization_id == current_user.organization_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    # Retrieve ticket events and user names
    events = db.query(
        TicketEvent,
        User.full_name
    ).outerjoin(
        User,
        TicketEvent.user_id == User.id
    ).filter(
        TicketEvent.ticket_id == ticket.id
    ).order_by(
        TicketEvent.created_at.desc()
    ).all()

    return [
        TicketEventResponse(
            id=str(event.id),
            ticket_id=str(event.ticket_id),
            user_id=str(event.user_id) if event.user_id else None,
            event_type=event.event_type,
            old_value=event.old_value,
            new_value=event.new_value,
            created_at=event.created_at,
            user_name=user_name
        )
        for event, user_name in events
    ]


