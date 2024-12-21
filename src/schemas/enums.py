from enum import IntEnum, StrEnum


class SystemRoles(StrEnum):
    SUPERUSER = "superuser"
    ADMIN = "admin"


class ServiceWorkResults(IntEnum):
    SUCCESS = 1
    FAIL = 0
    ERROR = -1
