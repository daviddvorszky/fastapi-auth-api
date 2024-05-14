from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user import UserCreate

class CRUDUser:
    async def get_user(self, db: AsyncSession, user_id: int):
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def get_user_by_email(self, db: AsyncSession, email: str):
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create_user(self, db: AsyncSession, user_in: UserCreate):
        db_user = User(email=user_in.email, hashed_password=user_in.hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

crud_user = CRUDUser()
