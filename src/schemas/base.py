from pydantic import BaseModel, ConfigDict


class OrmBasedDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
