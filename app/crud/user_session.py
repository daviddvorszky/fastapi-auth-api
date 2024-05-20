import ulid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_session import UserSession
from app.schemas.user_session import SessionCreate


class CRUDUserSession:
    async def get_session(self, db: AsyncSession, session_id: int):
        raise NotImplementedError()

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


crud_session = CRUDUserSession()
