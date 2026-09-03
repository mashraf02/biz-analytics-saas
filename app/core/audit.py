"""
Audit logging helper. Call log_action() after any state-changing operation
you want tracked. Kept intentionally simple — a real production system might
send these to a separate log aggregator, but a DB table is the right level
of complexity for this MVP.
"""

from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    tenant_id: int,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: int | None = None,
    details: str | None = None,
):
    entry = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    )
    db.add(entry)
    # Deliberately not committing here — caller's existing db.commit()
    # (for the actual create) will include this in the same transaction.
