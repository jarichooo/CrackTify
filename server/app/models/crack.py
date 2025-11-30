from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.database.db import Base

class Crack(Base):
    __tablename__ = "cracks"

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("images.id"))
    description = Column(String(255), nullable=True)
    severity = Column(String(50))
    detected_at = Column(DateTime, default=datetime.now(timezone.utc))

    image = relationship("Image", back_populates="cracks")
