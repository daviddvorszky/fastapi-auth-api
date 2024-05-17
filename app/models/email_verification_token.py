from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.custom_types import ULIDType


class EmailVerificationToken(Base):
    __tablename__ = 'email_verification_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ULIDType(), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="email_verification_tokens")
