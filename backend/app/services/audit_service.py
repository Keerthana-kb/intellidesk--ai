
from app.models.audit_log import AuditLog


def create_audit_log(
    db,
    organization_id,
    user_id,
    action,
    entity_type,
    entity_id=None,
    details=None,
    ip_address=None
):
    audit_log = AuditLog(
        organization_id=organization_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        details=details,
        ip_address=ip_address
    )

    db.add(audit_log)

    return audit_log
