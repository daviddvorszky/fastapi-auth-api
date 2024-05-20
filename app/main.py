from fastapi import FastAPI
from app.api.v1.endpoints import auth, users, health

app = FastAPI()

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(health.router, prefix="/api/v1", tags=["health"])
