from datetime import timedelta

from pydantic import BaseModel

from app.core.config import settings


class JWTSettings(BaseModel):
    authjwt_secret_key: str = settings.SECRET_KEY
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access"}
    access_expires: int = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires: int = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)