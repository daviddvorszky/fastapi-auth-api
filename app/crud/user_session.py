import ulid
from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.user_session import SessionCreate


class CRUDUserSession:
    async def get_session(self, db: AsyncSession, session_id: int):
        raise NotImplementedError()
    
    async def get_session_by_token(self, db: AsyncSession, refresh_token: str) -> Optional[UserSession]:
        result = await db.execute(select(UserSession).filter(UserSession.refresh_token == refresh_token))
        return result.scalars().first()

    async def create_session(self, db: AsyncSession, session_data: SessionCreate):
        session = UserSession(
            user_id=ulid.from_str(session_data.user_id),
            refresh_token=session_data.refresh_token,
            ip_address=session_data.ip_address,
            user_agent=session_data.user_agent,
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session
    
    async def deactivate_session(self, db: AsyncSession, refresh_token: str):
        session = await self.get_session_by_token(db, refresh_token)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found in crud"
            )
        session.active = False
        db.add(session)
        await db.commit()
        await db.refresh(session)

    async def deactivate_all_sessions(self, db: AsyncSession, username: str):
        stmt = (
            update(UserSession)
            .where(UserSession.user_id == User.id, User.username == username)
            .values(active=False)
            .returning(UserSession)
        )
        await db.execute(stmt)
        await db.commit()

    async def is_session_active(self, db: AsyncSession, jti: str) -> Optional[bool]:
        session = await self.get_session_by_token(db, jti)
        
        if not session:
            return None
        
        return session.active
        


crud_session = CRUDUserSession()
