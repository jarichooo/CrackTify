from sqlalchemy import Column, Integer, ForeignKey, DateTime
from datetime import datetime, timezone
from .base import Base

class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    joined_at = Column(DateTime, default=datetime.now(timezone.utc))
