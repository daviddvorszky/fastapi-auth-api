import asyncio
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from app.core.token_handler import schedule_clean_up
from app.api.v1.endpoints import auth, health, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(schedule_clean_up())
    yield
    print("After")


app = FastAPI(lifespan=lifespan)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
