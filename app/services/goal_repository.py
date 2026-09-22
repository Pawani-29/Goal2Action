"""Database-agnostic persistence contract for Goal domain objects."""

from abc import ABC, abstractmethod

from app.models import Goal


class GoalAlreadyExistsError(ValueError):
    """Raised when attempting to create a goal whose ID is already stored."""


class GoalNotFoundError(KeyError):
    """Raised when an update targets a goal that does not exist."""


class GoalRepository(ABC):
    """Persistence boundary for Goal without exposing database-specific details."""

    @abstractmethod
    def create(self, goal: Goal) -> Goal:
        """Persist a new goal and return its validated stored representation."""

    @abstractmethod
    def get_by_id(self, goal_id: str) -> Goal | None:
        """Return a goal by ID, or ``None`` when it is not present."""

    @abstractmethod
    def list_by_user(self, user_id: str) -> list[Goal]:
        """Return all goals belonging to one user, ordered by creation time."""

    @abstractmethod
    def update(self, goal: Goal) -> Goal:
        """Replace an existing goal or raise ``GoalNotFoundError``."""

    @abstractmethod
    def delete(self, goal_id: str) -> bool:
        """Delete a goal and return whether a stored goal was removed."""

