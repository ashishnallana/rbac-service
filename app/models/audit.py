from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True) # Optional because login failed attempts might not have user id
    action = Column(String, nullable=False)
    status = Column(String, nullable=False) # e.g. success, failure
    ip = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
