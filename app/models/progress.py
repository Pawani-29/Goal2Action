"""Append-only execution history and supporting evidence models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .enums import EvidenceStatus, EvidenceType, ProgressEventType, TaskStatus
from .validation import (
    require_enum,
    require_non_empty,
    require_non_negative,
    require_utc_datetime,
    utc_now,
)


@dataclass(frozen=True, slots=True)
class ProgressEvent:
    """An immutable, append-only record of an execution observation or update."""

    id: str
    goal_id: str
    event_type: ProgressEventType
    reported_by: str
    task_id: str | None = None
    occurred_at: datetime = field(default_factory=utc_now)
    status_before: TaskStatus | None = None
    status_after: TaskStatus | None = None
    actual_minutes: int | None = None
    completion_percent: float | None = None
    note: str = ""
    blocker: str | None = None
    evidence_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate immutable event identity, event vocabulary, and measurements."""

        for field_name, value in (("id", self.id), ("goal_id", self.goal_id), ("reported_by", self.reported_by)):
            require_non_empty(value, field_name)
        if self.task_id is not None:
            require_non_empty(self.task_id, "task_id")
        require_enum(self.event_type, ProgressEventType, "event_type")
        require_utc_datetime(self.occurred_at, "occurred_at")
        for field_name, value in (("status_before", self.status_before), ("status_after", self.status_after)):
            if value is not None:
                require_enum(value, TaskStatus, field_name)
        if self.actual_minutes is not None:
            require_non_negative(self.actual_minutes, "actual_minutes")
        if self.completion_percent is not None and not 0 <= self.completion_percent <= 100:
            raise ValueError("completion_percent must be between 0 and 100")


@dataclass(slots=True)
class Evidence:
    """A typed reference that supports a goal or task progress assertion."""

    id: str
    goal_id: str
    type: EvidenceType
    summary: str
    source_reference: str
    submitted_by: str
    task_id: str | None = None
    progress_event_id: str | None = None
    status: EvidenceStatus = EvidenceStatus.UNVERIFIED
    captured_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate evidence links, its controlled vocabulary, and timestamp."""

        for field_name, value in (("id", self.id), ("goal_id", self.goal_id), ("summary", self.summary), ("source_reference", self.source_reference), ("submitted_by", self.submitted_by)):
            require_non_empty(value, field_name)
        for field_name, value in (("task_id", self.task_id), ("progress_event_id", self.progress_event_id)):
            if value is not None:
                require_non_empty(value, field_name)
        require_enum(self.type, EvidenceType, "type")
        require_enum(self.status, EvidenceStatus, "status")
        require_utc_datetime(self.captured_at, "captured_at")

