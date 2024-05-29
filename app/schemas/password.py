from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.validators import validate_password


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(min_length=8)
    should_logout: bool = Field()

    @field_validator("new_password")
    def validate_password(cls, v):
        return validate_password(v)


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)
    should_logout: bool = Field()

    @field_validator("new_password")
    def validate_password(cls, v):
        return validate_password(v)
