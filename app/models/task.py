"""Task domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from .enums import Priority, TaskStatus
from .validation import (
    require_enum,
    require_non_empty,
    require_non_negative,
    require_utc_datetime,
    utc_now,
)


@dataclass(slots=True)
class Task:
    """An actionable, ordered unit of work associated with a goal and plan."""

    id: str
    goal_id: str
    plan_id: str
    title: str
    parent_task_id: str | None = None
    description: str = ""
    status: TaskStatus = TaskStatus.PROPOSED
    priority: Priority = Priority.MEDIUM
    estimate_minutes: int = 0
    due_at: datetime | None = None
    dependencies: list[str] = field(default_factory=list)
    sequence: int = 0
    completion_criteria: list[str] = field(default_factory=list)
    blocker_reason: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        """Validate task identity, enum values, estimates, and timestamps."""

        for field_name, value in (("id", self.id), ("goal_id", self.goal_id), ("plan_id", self.plan_id), ("title", self.title)):
            require_non_empty(value, field_name)
        if self.parent_task_id is not None:
            require_non_empty(self.parent_task_id, "parent_task_id")
        require_enum(self.status, TaskStatus, "status")
        require_enum(self.priority, Priority, "priority")
        require_non_negative(self.estimate_minutes, "estimate_minutes")
        require_non_negative(self.sequence, "sequence")
        require_utc_datetime(self.created_at, "created_at")
        require_utc_datetime(self.updated_at, "updated_at")
        if self.due_at is not None:
            require_utc_datetime(self.due_at, "due_at")

