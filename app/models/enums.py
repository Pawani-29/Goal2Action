"""Closed vocabularies used by the Goal2Action domain."""

from enum import Enum


class GoalStatus(str, Enum):
    """Lifecycle states for a student outcome."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ACHIEVED = "achieved"
    ABANDONED = "abandoned"
    EXPIRED = "expired"


class TaskStatus(str, Enum):
    """Execution states for a task in a plan."""

    PROPOSED = "proposed"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class PlanStatus(str, Enum):
    """Lifecycle states for a versioned plan."""

    DRAFT = "draft"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    COMPLETED = "completed"
    INVALIDATED = "invalidated"


class ProgressEventType(str, Enum):
    """Kinds of immutable execution-history entries."""

    STATUS_UPDATE = "status_update"
    EFFORT_LOGGED = "effort_logged"
    CHECKPOINT_REACHED = "checkpoint_reached"
    DEADLINE_MISSED = "deadline_missed"
    BLOCKER_REPORTED = "blocker_reported"
    CONTEXT_CHANGED = "context_changed"


class EvidenceType(str, Enum):
    """Sources that may support a progress claim."""

    USER_NOTE = "user_note"
    ARTIFACT_REFERENCE = "artifact_reference"
    TOOL_RESULT = "tool_result"
    CALENDAR_EVENT = "calendar_event"
    KNOWLEDGE_REFERENCE = "knowledge_reference"


class EvidenceStatus(str, Enum):
    """Verification state of submitted evidence."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Priority(str, Enum):
    """Relative importance assigned to a goal or task."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(str, Enum):
    """Severity levels for plan-feasibility assessments."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

