from fastapi import HTTPException


class Http500(HTTPException):
    def __init__(self, detail="Internal server error", headers=None) -> None:
        super().__init__(500, detail, headers)


class Http400(HTTPException):
    def __init__(self, detail=None, headers=None) -> None:
        super().__init__(400, detail, headers)
