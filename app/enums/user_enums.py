from enum import Enum


class UserRole(str, Enum):
    """Role assigned to a user. Inheriting from `str` makes it JSON friendly."""

    ADMIN = "admin"
    USER = "user"


class UserStatus(str, Enum):
    """Lifecycle status of a user account."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
