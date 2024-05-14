from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.User)
async def create_user(user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    user = await crud.crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The user with this email already exists.",
        )
    user = await crud.crud_user.create_user(db, user_in=user_in)
    return user