from pydantic import BaseModel


class TokenInfo(BaseModel):
    access: str
    refresh: str | None = None
