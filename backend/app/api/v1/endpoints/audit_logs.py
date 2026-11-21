
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.api.deps import get_current_user, require_roles

router = APIRouter()


@router.get("/", response_model=list[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    logs = db.query(
        AuditLog,
        User.full_name
    ).outerjoin(
        User,
        AuditLog.user_id == User.id
    ).filter(
        AuditLog.organization_id == current_user.organization_id
    ).order_by(
        AuditLog.created_at.desc()
    ).all()

    return [
        AuditLogResponse(
            id=str(log.id),
            user_id=str(log.user_id) if log.user_id else None,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            ip_address=log.ip_address,
            created_at=log.created_at,
            user_name=user_name
        )
        for log, user_name in logs
    ]
