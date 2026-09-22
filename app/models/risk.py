"""Risk-assessment domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from .enums import RiskLevel
from .validation import require_enum, require_non_empty, require_non_negative, require_utc_datetime, utc_now


@dataclass(slots=True)
class RiskAssessment:
    """A point-in-time assessment of whether remaining work fits available time."""

    id: str
    goal_id: str
    level: RiskLevel
    reason: str
    remaining_minutes: int
    available_minutes: int
    recommended_action: str
    assessed_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Validate assessment identity, risk vocabulary, capacity values, and time."""

        for field_name, value in (("id", self.id), ("goal_id", self.goal_id), ("reason", self.reason), ("recommended_action", self.recommended_action)):
            require_non_empty(value, field_name)
        require_enum(self.level, RiskLevel, "level")
        require_non_negative(self.remaining_minutes, "remaining_minutes")
        require_non_negative(self.available_minutes, "available_minutes")
        require_utc_datetime(self.assessed_at, "assessed_at")

