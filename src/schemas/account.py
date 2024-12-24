from pydantic import BaseModel
from typing import Any, List, Dict


class Meta(BaseModel):
    current_page: int
    page_size: int
    total_count: int
    total_pages: int


class LoginHistoryResponse(BaseModel):
    data: List[Dict[str, str]]
    meta: Meta
