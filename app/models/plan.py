"""Plan domain model."""

from dataclasses import dataclass, field
from datetime import datetime

from .enums import PlanStatus
from .validation import require_enum, require_non_empty, require_utc_datetime, utc_now


@dataclass(slots=True)
class Plan:
    """A versioned planning snapshot for a goal, linked to its predecessor."""

    id: str
    goal_id: str
    revision: int
    status: PlanStatus = PlanStatus.DRAFT
    predecessor_plan_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)
    activated_at: datetime | None = None
    superseded_at: datetime | None = None
    planning_rationale: str = ""
    assumptions: list[str] = field(default_factory=list)
    schedule_window: tuple[datetime, datetime] | None = None

    def __post_init__(self) -> None:
        """Validate versioning links, timestamps, and schedule-window shape."""

        require_non_empty(self.id, "id")
        require_non_empty(self.goal_id, "goal_id")
        require_enum(self.status, PlanStatus, "status")
        require_utc_datetime(self.created_at, "created_at")
        if self.revision < 1:
            raise ValueError("revision must be at least 1")
        if self.predecessor_plan_id is not None:
            require_non_empty(self.predecessor_plan_id, "predecessor_plan_id")
        for field_name, value in (("activated_at", self.activated_at), ("superseded_at", self.superseded_at)):
            if value is not None:
                require_utc_datetime(value, field_name)
        if self.schedule_window is not None:
            start, end = self.schedule_window
            require_utc_datetime(start, "schedule_window start")
            require_utc_datetime(end, "schedule_window end")
            if end <= start:
                raise ValueError("schedule_window end must be after its start")

