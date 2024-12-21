from pydantic import UUID4

from .base import OrmBasedDTO


class CreateRoleDTO(OrmBasedDTO):
    title: str


class UpdateRoleDTO(CreateRoleDTO): ...


class ReadRoleDTO(CreateRoleDTO):
    id: UUID4
