from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, nullable=False)
    plan = Column(String, nullable=False, default="free")  # "free" or "pro"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
