from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.custom_types import ULIDType


class MFA(Base):
    __tablename__ = "mfa"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ULIDType(), ForeignKey("users.id"), nullable=False)
    mfa_type = Column(String, nullable=False)
    secret = Column(String)
    enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="mfa")
