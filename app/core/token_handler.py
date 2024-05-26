import asyncio
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable, Optional

from app.core.config import settings
from app.schemas.token import JWTSettings
from app.db.session import get_db
from app.crud.user_session import crud_session


@AuthJWT.load_config
def get_config():
    return JWTSettings()


denylist = []

def clean_up_exipred_access_tokens():
    now = int(datetime.now().timestamp())
    for item in denylist:
        expired = item["exp"] < now
        if expired:
            denylist.remove(item)


async def schedule_clean_up():
    while True:
        clean_up_exipred_access_tokens()
        await asyncio.sleep(settings.DENIED_TOKEN_CLEAN_UP_MINUTES)


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token["jti"]
    return any(d["jti"] == jti for d in denylist)


async def verify_active_refresh_token(Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)) -> dict:
    Authorize.jwt_refresh_token_required()
    refresh_token = Authorize.get_raw_jwt()

    active = crud_session.is_session_active(db, refresh_token["jti"])

    if active:
        return refresh_token
    elif active is False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive refresh token",
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid refresh token",
        )


def get_verify_access_token_dependency(required: bool = True) -> Callable:
    async def verify_access_token(Authorize: AuthJWT = Depends(), required=True) -> Optional[dict]:
        if required:
            Authorize.jwt_required()
        else:
            Authorize.jwt_optional()
        access_token = Authorize.get_raw_jwt()
        return access_token
    
    return verify_access_token


async def invalidate_access_token(access_token: Optional[dict]):
    if access_token:
        jti = access_token["jti"]
        exp = access_token["exp"]
        denylist.append({"jti": jti, "exp": exp})


