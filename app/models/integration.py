from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)

    provider = Column(String, nullable=False)          # e.g. "facebook"
    connected = Column(Boolean, default=False)
    access_token = Column(String, nullable=True)        # would store the real OAuth token later
    external_account_id = Column(String, nullable=True) # e.g. Facebook Page ID

    last_synced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
