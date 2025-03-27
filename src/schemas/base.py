from pydantic import BaseModel, ConfigDict, Field


class OrmBasedDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    page_size: int = Field(50, description="Количество объектов на странице", ge=1, le=100)
    page_number: int = Field(1, description="Номер страницы", ge=1, le=250)
