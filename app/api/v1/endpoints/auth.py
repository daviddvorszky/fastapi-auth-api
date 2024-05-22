import asyncio
from datetime import datetime
import jwt

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.user import crud_user
from app.crud.user_session import crud_session
from app.db.session import get_db
from app.models.custom_types import ULIDType
from app.schemas.token import JWTSettings
from app.schemas.user import UserLogin
from app.schemas.user_session import SessionCreate

router = APIRouter()


@AuthJWT.load_config
def get_config():
    return JWTSettings()


denylist = []


@AuthJWT.token_in_denylist_loader
def check_if_token_in_denylist(decrypted_token):
    jti = decrypted_token["jti"]
    return any(d["jti"] == jti for d in denylist)


@router.post("/login")
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: UserLogin = Depends(),
    Authorize: AuthJWT = Depends(),
    request: Request = None,
):
    user = await crud_user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive",
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not verified",
        )

    access_token = Authorize.create_access_token(subject=user.username)
    refresh_token = Authorize.create_refresh_token(subject=user.username)
    decoded_token = jwt.decode(refresh_token, settings.SECRET_KEY)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    print(f"decoded jti: {decoded_token['jti']}")

    session_data = SessionCreate(
        user_id=str(user.id),
        refresh_token=decoded_token['jti'],
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
    )

    _ = await crud_session.create_session(db, session_data)

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/access_token")
async def refresh_access_token(
    Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)
):
    # Validate refresh token
    Authorize.jwt_refresh_token_required()
    username = Authorize.get_jwt_subject()
    user = await crud_user.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Invalidate previous access token
    Authorize.jwt_optional()
    access_token = Authorize.get_raw_jwt()
    if access_token:
        jti = access_token["jti"]
        exp = access_token["exp"]
        denylist.append({"jti": jti, "exp": exp})
        Authorize.unset_access_cookies()

    access_token = Authorize.create_access_token(subject=user.username)
    Authorize.set_access_cookies(access_token)

    return {"access_token": access_token}


@router.delete("/logout")
async def logout(Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)
):
    Authorize.jwt_refresh_token_required()
    refresh_token = Authorize.get_raw_jwt()
    await crud_session.deactivate_session(db, refresh_token['jti'])

    Authorize.jwt_optional()
    access_token = Authorize.get_raw_jwt()
    if access_token:
        jti = access_token["jti"]
        exp = access_token["exp"]
        denylist.append({"jti": jti, "exp": exp})

    Authorize.unset_jwt_cookies()

    return {"msg": "Successfully logout"}


@router.delete("/logout_all")
async def logout_all(Authorize: AuthJWT = Depends(), db: AsyncSession = Depends(get_db)):
    Authorize.jwt_refresh_token_required()
    refresh_token = Authorize.get_raw_jwt()
    username = refresh_token['sub']
    await crud_session.deactivate_all_sessions(db, username)

    Authorize.jwt_optional()
    access_token = Authorize.get_raw_jwt()
    if access_token:
        jti = access_token["jti"]
        exp = access_token["exp"]
        denylist.append({"jti": jti, "exp": exp})

    Authorize.unset_jwt_cookies()

    return {"msg": "Successfully logout"}


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
