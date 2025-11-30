from datetime import datetime, timezone, timedelta
from sqlalchemy import Column, Integer, String, DateTime
from app.database.db import Base

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False)
    otp = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), default=lambda _: datetime.now(timezone.utc) + timedelta(minutes=5))
