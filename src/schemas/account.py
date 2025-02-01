from typing import List

from pydantic import BaseModel


class HistoryMeta(BaseModel):
    current_page: int
    page_size: int
    total_count: int
    total_pages: int


class HistoryItem(BaseModel):
    date_time: str
    ip_address: str
    user_agent: str    


class LoginHistoryOut(BaseModel):
    data: List[HistoryItem]
    meta: HistoryMeta
