from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database.db import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    image_base64 = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="images")
    cracks = relationship("Crack", back_populates="image")
