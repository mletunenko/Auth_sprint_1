from datetime import datetime

from pydantic import UUID4, BaseModel


class LoginHistory(BaseModel):
    user_id: UUID4
    timestamp: datetime
    ip_address: str
    user_agent: str
