"""User context domain model."""

from dataclasses import dataclass, field
from datetime import datetime, time

from .validation import require_non_empty, require_non_negative, require_utc_datetime, utc_now


@dataclass(slots=True)
class UserContext:
    """V1 planning constraints supplied by a user, without persistence concerns."""

    user_id: str
    timezone: str
    availability_windows: list[tuple[time, time]] = field(default_factory=list)
    workload_limits: dict[str, int] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Validate context identity, local availability intervals, and limits."""

        require_non_empty(self.user_id, "user_id")
        require_non_empty(self.timezone, "timezone")
        require_utc_datetime(self.updated_at, "updated_at")
        for start, end in self.availability_windows:
            if not isinstance(start, time) or not isinstance(end, time):
                raise ValueError("availability_windows must contain time pairs")
            if end <= start:
                raise ValueError("availability window end must be after its start")
        for limit_name, limit_value in self.workload_limits.items():
            require_non_empty(limit_name, "workload_limits key")
            require_non_negative(limit_value, f"workload_limits[{limit_name}]")

