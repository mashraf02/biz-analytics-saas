from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    action = Column(String, nullable=False)       # e.g. "product_created"
    resource_type = Column(String, nullable=False) # e.g. "product"
    resource_id = Column(Integer, nullable=True)
    details = Column(String, nullable=True)         # short human-readable summary

    created_at = Column(DateTime(timezone=True), server_default=func.now())
