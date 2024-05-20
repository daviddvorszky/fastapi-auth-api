from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class CRUDUser:
    async def get_user(self, db: AsyncSession, user_id: str):
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, db: AsyncSession, email: str):
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_user_by_username(self, db: AsyncSession, username: str):
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def get_user_by_username_or_email(
        self, db: AsyncSession, username: str, email: str
    ):
        result = await db.execute(
            select(User).filter(
                or_(User.username.like(username), User.email.like(email))
            )
        )
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, user_in: UserCreate):
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def authenticate(self, db: AsyncSession, username: str, password: str):
        user = await self.get_user_by_username_or_email(
            db, username=username, email=username
        )
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


crud_user = CRUDUser()
