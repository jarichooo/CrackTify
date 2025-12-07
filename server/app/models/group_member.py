from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from app.database.db import Base
from sqlalchemy.orm import relationship

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    joined_at = Column(DateTime, default=datetime.now(timezone.utc))

    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")