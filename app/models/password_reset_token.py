from datetime import datetime, timedelta
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.custom_types import ULIDType


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ULIDType(), ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, default=datetime.now() + timedelta(days=1))
    created_at = Column(DateTime, default=func.now())
    used = Column(Boolean, default=False)

    user = relationship("User", back_populates="password_reset_tokens")
