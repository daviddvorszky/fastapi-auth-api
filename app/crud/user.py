from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash

class CRUDUser:
    async def get_user(self, db: AsyncSession, user_id: int):
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, db: AsyncSession, email: str):
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, user_in: UserCreate):
        hashed_password = get_password_hash(user_in.password)
        db_user = User(email=user_in.email, hashed_password=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def authenticate(self, db: AsyncSession, email: str, password: str):
        user = await self.get_user_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

crud_user = CRUDUser()
