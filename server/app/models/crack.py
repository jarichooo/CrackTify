from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean, Float
from sqlalchemy.orm import relationship
from app.database.db import Base

class Crack(Base):
    __tablename__ = "cracks"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    image_base64 = Column(Text, nullable=False)
    # probability = Column(Float, nullable=True)
    severity = Column(String(50))
    visibility = Column(Boolean, default=False)
    detected_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="cracks")
    group = relationship("Group", back_populates="cracks")