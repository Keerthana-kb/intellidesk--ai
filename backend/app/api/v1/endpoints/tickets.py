
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
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



