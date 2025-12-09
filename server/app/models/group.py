from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.db import Base

class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    pin = Column(String(255), nullable=False)
    admin_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    users = relationship("User", secondary="group_members")

    cracks = relationship("CrackGroup", back_populates="group", cascade="all, delete-orphan")
