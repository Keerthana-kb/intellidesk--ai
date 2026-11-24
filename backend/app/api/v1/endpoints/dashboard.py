from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.ticket import Ticket

router = APIRouter()

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    organization_id = current_user.organization_id

    total_tickets = db.query(Ticket).filter(
        Ticket.organization_id == organization_id
    ).count()

    open_tickets = db.query(Ticket).filter(
        Ticket.organization_id == organization_id,
        Ticket.status == "open"
    ).count()

    in_progress_tickets = db.query(Ticket).filter(
        Ticket.organization_id == organization_id,
        Ticket.status == "in_progress"
    ).count()

    resolved_tickets = db.query(Ticket).filter(
        Ticket.organization_id == organization_id,
        Ticket.status == "resolved"
    ).count()

    closed_tickets = db.query(Ticket).filter(
        Ticket.organization_id == organization_id,
        Ticket.status == "closed"
    ).count()

    sla_breaches = db.query(Ticket).filter(
        Ticket.organization_id == organization_id,
        (Ticket.response_breached == True) |
        (Ticket.resolution_breached == True)
    ).count()

    return {
        "total_tickets": total_tickets,
        "open_tickets": open_tickets,
        "in_progress_tickets": in_progress_tickets,
        "resolved_tickets": resolved_tickets,
        "closed_tickets": closed_tickets,
        "sla_breaches": sla_breaches
    }