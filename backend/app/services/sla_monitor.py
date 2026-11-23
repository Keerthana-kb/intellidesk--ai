
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.ticket_event import TicketEvent
from app.models.user import User
from app.services.audit_service import create_audit_log


def check_sla_breaches(db: Session):
    current_time = datetime.now(timezone.utc)

    breached_count = 0

    # Find tickets where first response is overdue
    response_tickets = db.query(Ticket).filter(
        Ticket.first_response_at.is_(None),
        Ticket.response_due_at <= current_time,
        Ticket.response_breached.is_(False)
    ).all()

    for ticket in response_tickets:

        ticket.response_breached = True

        response_event = TicketEvent(
            ticket_id=ticket.id,
            user_id=None,
            event_type="response_sla_breached",
            old_value="False",
            new_value="True"
        )

        db.add(response_event)

        create_audit_log(
            db=db,
            organization_id=ticket.organization_id,
            user_id=None,
            action="response_sla_breached",
            entity_type="ticket",
            entity_id=ticket.id,
            details={
                "priority": ticket.priority,
                "response_due_at": ticket.response_due_at.isoformat()
            }
        )

        breached_count += 1

    # Find unresolved tickets where resolution is overdue
    resolution_tickets = db.query(Ticket).filter(
        Ticket.resolved_at.is_(None),
        Ticket.resolution_due_at <= current_time,
        Ticket.resolution_breached.is_(False)
    ).all()

    for ticket in resolution_tickets:

        ticket.resolution_breached = True

        resolution_event = TicketEvent(
            ticket_id=ticket.id,
            user_id=None,
            event_type="resolution_sla_breached",
            old_value="False",
            new_value="True"
        )

        db.add(resolution_event)

        create_audit_log(
            db=db,
            organization_id=ticket.organization_id,
            user_id=None,
            action="resolution_sla_breached",
            entity_type="ticket",
            entity_id=ticket.id,
            details={
                "priority": ticket.priority,
                "resolution_due_at": ticket.resolution_due_at.isoformat()
            }
        )

        breached_count += 1

    db.commit()

    return {
        "message": "SLA breach check completed",
        "breaches_detected": breached_count
    }
