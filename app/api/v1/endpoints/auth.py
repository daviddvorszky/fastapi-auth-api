import jwt

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.config import settings
from app.crud.password_reset_token import crud_password_reset_token
from app.crud.user import crud_user
from app.crud.user_session import crud_session
from app.db.session import get_db
from app.core.token_handler import verify_active_refresh_token, get_verify_access_token_dependency, invalidate_access_token
from app.models.custom_types import ULIDType
from app.schemas.user import User, UserLogin, UserCreate
from app.schemas.user_session import SessionCreate
from app.schemas.password import PasswordChange, PasswordResetRequest, PasswordResetConfirm
from app.core.security import verify_password


router = APIRouter()


@router.post("/register", response_model=User)
async def create_user(
    user_in: UserCreate, db: AsyncSession = Depends(get_db)
):
    user = await crud_user.get_user_by_username_or_email(
        db, username=user_in.username, email=user_in.email
    )
    if user:
        existing_field = "username" if user.username == user_in.username else "email"
        error_msg = f"A user with this {existing_field} already exists"
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_msg,
        )
    user = await crud_user.create_user(db, user_in=user_in)
    return user


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
    refresh_token: dict = Depends(verify_active_refresh_token),
    access_token: dict = Depends(get_verify_access_token_dependency(required=False)),
    Authorize: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_db),
):
    username = refresh_token['sub']
    user = await crud_user.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    await invalidate_access_token(access_token)
    access_token = Authorize.create_access_token(subject=user.username)
    Authorize.set_access_cookies(access_token)

    return {"access_token": access_token}


@router.delete("/logout")
async def logout(
    refresh_token: dict = Depends(verify_active_refresh_token),
    access_token: dict = Depends(get_verify_access_token_dependency(required=False)),
    Authorize: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_db),
):
    await crud_session.deactivate_session(db, refresh_token['jti'])
    await invalidate_access_token(access_token)
    Authorize.unset_jwt_cookies()

    return {"msg": "Successfully logout"}


@router.delete("/logout_all")
async def logout_all(
    refresh_token: dict = Depends(verify_active_refresh_token),
    access_token: Optional[dict] = Depends(get_verify_access_token_dependency(required=False)),
    Authorize: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_db),
):
    await crud_session.deactivate_all_sessions(db=db, username=refresh_token['sub'])
    await invalidate_access_token(access_token)
    Authorize.unset_jwt_cookies()

    return {"msg": "Successfully logout"}


@router.post("/password-reset/request")
async def password_reset_request(data: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get_user_by_email(db, email=data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found"
        )
    token = await crud_user.create_password_reset_token(db, str(user.id))
    # TODO: Send email
    # await send_password_reset_email(user.email, token)
    print(f"email: {user.email}, token: {token.token}")
    return {"msg": "Password reset email sent"}


@router.post("/password-reset/confirm")
async def password_reset_confirm(data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)):
    token = await crud_password_reset_token.get_token_by_token(db, token=data.token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid reset token"
        )
    elif token.used:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been used already"
        )
    elif token.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    
    user = await crud_user.update_password(db, user_id=str(token.user_id), password=data.new_password)
    await crud_password_reset_token.invalidate_token(db, token)

    if data.should_logout:
        await crud_session.deactivate_all_sessions(db, user.username)

    return {"msg": "Password reset successful"}


@router.post("/password-change")
async def password_change(
    data: PasswordChange,
    access_token: Optional[dict] = Depends(get_verify_access_token_dependency(required=False)),
    Authorize: AuthJWT = Depends(),
    db: AsyncSession = Depends(get_db),
):

    username= access_token['sub']
    user = await crud_user.get_user_by_username(db, username)
    if not verify_password(data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    user = await crud_user.update_password(db, str(user.id), data.new_password)
    if data.should_logout:
        await crud_session.deactivate_all_sessions(db, user.username)
        await invalidate_access_token(access_token)
        Authorize.unset_jwt_cookies()


    return {"msg": "Password change successful"}
