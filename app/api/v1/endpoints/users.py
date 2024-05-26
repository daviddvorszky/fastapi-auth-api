from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import crud_user
from app.db.session import get_db
from app.schemas import user as user_schema

router = APIRouter()


@router.post("/register", response_model=user_schema.User)
async def create_user(
    user_in: user_schema.UserCreate, db: AsyncSession = Depends(get_db)
):
    user = await crud_user.get_user_by_username_or_email(
        db, username=user_in.username, email=user_in.email
    )
    if user:
        existing_field = "username" if user.username == user_in.username else "email"
        error_msg = f"A user with this {existing_field} already exists"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_msg,
        )
    user = await crud_user.create_user(db, user_in=user_in)
    return user
