from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        func)
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.custom_types import ULIDType


class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ULIDType(), ForeignKey('users.id'), nullable=False)
    refresh_token = Column(String, nullable=False, unique=True)
    ip_address = Column(String(45))
    device_type = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    active = Column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="sessions")
