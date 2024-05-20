from pydantic import BaseModel, field_validator
from ulid import from_str


class SessionCreate(BaseModel):
    user_id: str
    refresh_token: str
    ip_address: str
    user_agent: str
