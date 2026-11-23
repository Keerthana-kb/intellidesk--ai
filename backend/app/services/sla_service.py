from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.sla_policy import SLAPolicy


def calculate_sla_deadlines(
    db: Session,
    organization_id,
    priority: str,
    created_at: datetime
):
    # Find the active SLA policy for this organization and priority
    sla_policy = db.query(SLAPolicy).filter(
        SLAPolicy.organization_id == organization_id,
        SLAPolicy.priority == priority,
        SLAPolicy.is_active.is_(True)
    ).first()

    if not sla_policy:
        return None

    # Calculate response deadline
    response_due_at = created_at + timedelta(
        minutes=sla_policy.response_time_minutes
    )

    # Calculate resolution deadline
    resolution_due_at = created_at + timedelta(
        minutes=sla_policy.resolution_time_minutes
    )

    return {
        "response_due_at": response_due_at,
        "resolution_due_at": resolution_due_at
    }