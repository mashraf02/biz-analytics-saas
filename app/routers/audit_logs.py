from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


class AuditLogOut(BaseModel):
    id: int
    action: str
    resource_type: str
    resource_id: int | None
    details: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[AuditLogOut])
def list_audit_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.tenant_id == current_user.tenant_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
