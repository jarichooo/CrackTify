from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database.db import Base

class CrackGroup(Base):
    __tablename__ = "crack_groups"

    id = Column(Integer, primary_key=True)
    crack_id = Column(Integer, ForeignKey("cracks.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    crack = relationship("Crack", back_populates="groups")
    group = relationship("Group", back_populates="cracks")
