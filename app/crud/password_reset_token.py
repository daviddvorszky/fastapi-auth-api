from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.password_reset_token import PasswordResetToken


class CRUDPasswordResetToken:
    async def get_token_by_token(self, db: AsyncSession, token: str):
        result = await db.execute(select(PasswordResetToken).filter(PasswordResetToken.token == token))
        return result.scalars().first()
    
    async def invalidate_token(self, db: AsyncSession, token: PasswordResetToken):
        token.used = True
        db.add(token)
        await db.commit()
        await db.refresh(token)
    

crud_password_reset_token = CRUDPasswordResetToken()