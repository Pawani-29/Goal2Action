"""Application tool for creating and persisting a Goal."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.models import Goal, GoalStatus, Priority
from app.services import GoalAlreadyExistsError, GoalRepository


class CreateGoalErrorCode(str, Enum):
    """Failure categories returned by the create-goal tool boundary."""

    INVALID_GOAL = "invalid_goal"
    DUPLICATE_GOAL_ID = "duplicate_goal_id"
    REPOSITORY_ERROR = "repository_error"


@dataclass(slots=True)
class CreateGoalInput:
    """Structured input accepted by ``create_goal`` for all Goal V1 fields."""

    id: str
    user_id: str
    title: str
    description: str = ""
    status: GoalStatus = GoalStatus.DRAFT
    priority: Priority = Priority.MEDIUM
    success_criteria: list[str] = field(default_factory=list)
    target_date: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    constraints: dict[str, str] = field(default_factory=dict)
    tags: set[str] = field(default_factory=set)
    version: int = 1


@dataclass(frozen=True, slots=True)
class CreateGoalResult:
    """Structured success or failure result returned by ``create_goal``."""

    goal: Goal | None
    error_code: CreateGoalErrorCode | None = None
    message: str | None = None


def create_goal(repository: GoalRepository, data: CreateGoalInput) -> CreateGoalResult:
    """Validate structured input, persist its Goal through a repository, and report it.

    The repository is injected as the abstraction, so this tool has no knowledge
    of SQLite or any other storage implementation.
    """

    goal_arguments: dict[str, object] = {
        "id": data.id,
        "user_id": data.user_id,
        "title": data.title,
        "description": data.description,
        "status": data.status,
        "priority": data.priority,
        "success_criteria": list(data.success_criteria),
        "target_date": data.target_date,
        "constraints": dict(data.constraints),
        "tags": set(data.tags),
        "version": data.version,
    }
    if data.created_at is not None:
        goal_arguments["created_at"] = data.created_at
    if data.updated_at is not None:
        goal_arguments["updated_at"] = data.updated_at

    try:
        goal = Goal(**goal_arguments)  # type: ignore[arg-type]
    except ValueError as error:
        return CreateGoalResult(
            goal=None,
            error_code=CreateGoalErrorCode.INVALID_GOAL,
            message=str(error),
        )

    try:
        stored_goal = repository.create(goal)
    except GoalAlreadyExistsError as error:
        return CreateGoalResult(
            goal=None,
            error_code=CreateGoalErrorCode.DUPLICATE_GOAL_ID,
            message=str(error),
        )
    except Exception as error:
        return CreateGoalResult(
            goal=None,
            error_code=CreateGoalErrorCode.REPOSITORY_ERROR,
            message=str(error),
        )

    return CreateGoalResult(goal=stored_goal)

