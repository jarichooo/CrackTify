from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.database.db import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    title = Column(String(255))
    description = Column(String(255))
    generated_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="reports")
