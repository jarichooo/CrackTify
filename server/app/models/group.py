from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database.db import Base

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255))
    avatar_url = Column(String(255))
    admin_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
