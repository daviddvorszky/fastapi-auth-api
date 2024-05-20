import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    username: str = Field(min_length=4, max_length=32)
    email: EmailStr = Field(...)

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    @field_validator('password')
    def validate_password(cls, v):
        pattern = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$")
        if not pattern.match(v):
            raise ValueError(
                'Password must contain at least 1 uppercase letter, '
                '1 lowercase letter, 1 number, and 1 special character.'
            )
        return v

class UserLogin(BaseModel):
    username: str = Field(min_length=4, max_length=32)
    password: str = Field(...)

class UserInDB(UserBase):
    hashed_password: str = Field(...)

class User(UserBase):
    id: str = Field(..., exclude=True)
    is_active: bool = Field(...)
    is_verified: bool = Field(...)
    is_superuser: bool = Field(..., exclude=True)

    @field_validator('id', mode='before')
    def validate_id(cls, v):
        return str(v)

    class Config:
        from_attributes = True

class UserDetailed(User):
    id: str = Field(..., exclude=False)
    is_superuser: bool = Field(..., exclude=False)
