"""Small validation helpers shared by domain models.

These helpers intentionally contain only data invariants; they have no
persistence, service, or orchestration dependencies.
"""

from datetime import datetime
from enum import Enum
from typing import TypeVar


EnumT = TypeVar("EnumT", bound=Enum)


def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""

    from datetime import UTC

    return datetime.now(UTC)


def require_non_empty(value: str, field_name: str) -> None:
    """Require a non-blank string identifier or label."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def require_utc_datetime(value: datetime, field_name: str) -> None:
    """Require a timezone-aware datetime whose UTC offset is zero."""

    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError(f"{field_name} must be a timezone-aware UTC datetime")
    if value.utcoffset() is None or value.utcoffset().total_seconds() != 0:
        raise ValueError(f"{field_name} must be in UTC")


def require_enum(value: object, enum_type: type[EnumT], field_name: str) -> None:
    """Require a member of the declared enum, rejecting raw strings."""

    if not isinstance(value, enum_type):
        raise ValueError(f"{field_name} must be a {enum_type.__name__} value")


def require_non_negative(value: int | float, field_name: str) -> None:
    """Require a numeric value greater than or equal to zero."""

    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{field_name} must be non-negative")

