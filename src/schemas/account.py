from typing import Any, Dict, List

from pydantic import BaseModel


class Meta(BaseModel):
    current_page: int
    page_size: int
    total_count: int
    total_pages: int


class LoginHistoryResponse(BaseModel):
    data: List[Dict[str, str]]
    meta: Meta
