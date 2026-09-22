"""Goal domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from .enums import GoalStatus, Priority
from .validation import require_enum, require_non_empty, require_utc_datetime, utc_now


@dataclass(slots=True)
class Goal:
    """A student-owned outcome with success criteria and a target date."""

    id: str
    user_id: str
    title: str
    description: str = ""
    status: GoalStatus = GoalStatus.DRAFT
    priority: Priority = Priority.MEDIUM
    success_criteria: list[str] = field(default_factory=list)
    target_date: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    constraints: dict[str, str] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)
    version: int = 1

    def __post_init__(self) -> None:
        """Validate identifiers, lifecycle values, and temporal invariants."""

        require_non_empty(self.id, "id")
        require_non_empty(self.user_id, "user_id")
        require_non_empty(self.title, "title")
        require_enum(self.status, GoalStatus, "status")
        require_enum(self.priority, Priority, "priority")
        require_utc_datetime(self.created_at, "created_at")
        require_utc_datetime(self.updated_at, "updated_at")
        if self.target_date is not None:
            require_utc_datetime(self.target_date, "target_date")
        if self.version < 1:
            raise ValueError("version must be at least 1")

