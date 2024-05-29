from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_KEY: str
    DENIED_TOKEN_CLEAN_UP_MINUTES: int = 10
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24

    class Config:
        env_file = ".env"


settings = Settings()
