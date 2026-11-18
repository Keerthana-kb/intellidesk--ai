
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.ticket_comment import TicketComment
from app.db.session import get_db
from app.models.ticket import Ticket
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

    # Find ticket inside the user's organization
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user.organization_id
    ).first()

    # Check whether ticket exists
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Check whether status was provided
    if ticket_data.status is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status is required"
        )

    # Allowed ticket statuses
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

    # Update ticket status
    ticket.status = ticket_data.status

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

    allowed_priorities = ["low", "medium", "high", "critical"]

    if ticket_data.priority not in allowed_priorities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket priority"
        )

    ticket.priority = ticket_data.priority

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
    # Find ticket in the user's organization
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user.organization_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Create a new comment
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
    # Check whether ticket exists in user's organization
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.organization_id == current_user.organization_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )

    # Retrieve comments for this ticket
    comments = db.query(TicketComment).filter(
        TicketComment.ticket_id == ticket.id
    ).order_by(
        TicketComment.created_at.asc()
    ).all()

    return [
        TicketCommentResponse(
            id=str(comment.id),
            ticket_id=str(comment.ticket_id),
            user_id=str(comment.user_id),
            comment=comment.comment,
            created_at=comment.created_at
        )
        for comment in comments
    ]





