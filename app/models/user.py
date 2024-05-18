from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.custom_types import ULIDType
from app.models.user_session import UserSession
from app.models.password_reset_token import PasswordResetToken
from app.models.email_verification_token import EmailVerificationToken
from app.models.mfa import MFA


class User(Base):
    __tablename__ = 'users'

    id = Column(ULIDType(), default=lambda: ULIDType.create_ulid(), primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    sessions = relationship(UserSession.__name__, back_populates="user", cascade="all, delete-orphan")
    password_reset_tokens = relationship(PasswordResetToken.__name__, back_populates="user", cascade="all, delete-orphan")
    email_verification_tokens = relationship(EmailVerificationToken.__name__, back_populates="user", cascade="all, delete-orphan")
    mfa = relationship(MFA.__name__, back_populates="user", cascade="all, delete-orphan")
