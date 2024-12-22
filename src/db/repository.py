from typing import Any, List, Type

from pydantic import BaseModel
from sqlalchemy import Column, delete, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

import models


class AsyncBaseRepository:

    async def get(self, *args, **kwargs) -> BaseModel:
        raise NotImplementedError

    async def list(self, *args, **kwargs) -> BaseModel:
        raise NotImplementedError

    async def add(self, *args, **kwargs) -> models.Base:
        raise NotImplementedError

    async def update(self, *args, **kwargs) -> CursorResult[Any]:
        raise NotImplementedError

    async def delete(self, *args, **kwargs) -> CursorResult[Any]:
        raise NotImplementedError


class AsyncSqlAlchemyRepository(AsyncBaseRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, model: Type[models.Base]) -> list[models.Base]:
        stmt = select(model)
        result = await self.session.execute(stmt)
        result.scalars()
        return result.all()

    async def add(self, model_obj: models.Base) -> models.Base:
        async with self.session.begin():
            self.session.add(model_obj)
            await self.session.flush()
            await self.session.refresh(model_obj)
        return model_obj

    async def update(
        self, model: Type[models.Base], filter_col: Column, filter_val: Any, update_kws: dict
    ) -> models.Base:
        async with self.session.begin():
            stmt = update(model).where(filter_col == filter_val).values(**update_kws)
            result = await self.session.execute(stmt)
        return result

    async def delete(self, model: Type[models.Base], filter_col: Column, values: List[Any]):
        async with self.session.begin():
            if len(values) == 1:
                stmt = delete(model).where(filter_col == values[0])
            result = await self.session.execute(stmt)
        return result
