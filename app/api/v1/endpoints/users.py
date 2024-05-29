from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import crud_user
from app.db.session import get_db
from app.schemas import user as user_schema

router = APIRouter()


