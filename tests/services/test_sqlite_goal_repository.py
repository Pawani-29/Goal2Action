"""Tests for local SQLite Goal persistence."""

from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.models import Goal, GoalStatus, Priority
from app.services import GoalNotFoundError, SQLiteGoalRepository


NOW = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)


def make_goal(goal_id: str, user_id: str, title: str = "Pass calculus") -> Goal:
    """Build a complete valid goal fixture without relying on persistence state."""

    return Goal(
        id=goal_id,
        user_id=user_id,
        title=title,
        description="Prepare for the final exam",
        status=GoalStatus.ACTIVE,
        priority=Priority.HIGH,
        success_criteria=["Score at least 70 percent"],
        target_date=NOW,
        created_at=NOW,
        updated_at=NOW,
        constraints={"daily_minutes": "90"},
        tags={"math", "exam"},
        version=1,
    )


class SQLiteGoalRepositoryTests(unittest.TestCase):
    """Verify the database-agnostic repository contract through SQLite."""

    def setUp(self) -> None:
        """Create an isolated on-disk SQLite database for each test."""

        self._temporary_directory = TemporaryDirectory()
        self.database_path = Path(self._temporary_directory.name) / "goals.sqlite3"
        self.repository = SQLiteGoalRepository(self.database_path)

    def tearDown(self) -> None:
        """Remove the isolated temporary database."""

        self._temporary_directory.cleanup()

    def test_create_and_retrieve_goal(self) -> None:
        """A stored goal is reconstructed as the existing Goal domain model."""

        original = make_goal("goal-1", "user-1")
        self.repository.create(original)

        retrieved = self.repository.get_by_id("goal-1")

        self.assertEqual(retrieved, original)
        self.assertIsNot(retrieved, original)

    def test_list_goals_by_user(self) -> None:
        """Listing returns only the requested user's goals in creation order."""

        self.repository.create(make_goal("goal-1", "user-1"))
        self.repository.create(make_goal("goal-2", "user-1", "Finish essay"))
        self.repository.create(make_goal("goal-3", "user-2", "Read chapter"))

        goals = self.repository.list_by_user("user-1")

        self.assertEqual([goal.id for goal in goals], ["goal-1", "goal-2"])

    def test_update_goal(self) -> None:
        """Update replaces a persisted record and subsequent reads return it."""

        self.repository.create(make_goal("goal-1", "user-1"))
        revised = make_goal("goal-1", "user-1", "Pass calculus final")
        revised.status = GoalStatus.PAUSED
        revised.version = 2

        self.repository.update(revised)

        retrieved = self.repository.get_by_id("goal-1")
        self.assertEqual(retrieved, revised)

    def test_persistence_across_repository_instances(self) -> None:
        """A second repository instance reads data saved by the first instance."""

        self.repository.create(make_goal("goal-1", "user-1"))

        second_repository = SQLiteGoalRepository(self.database_path)

        self.assertEqual(second_repository.get_by_id("goal-1").title, "Pass calculus")

    def test_missing_goal_behavior(self) -> None:
        """Missing reads return None, missing deletes return False, and updates fail."""

        self.assertIsNone(self.repository.get_by_id("missing"))
        self.assertFalse(self.repository.delete("missing"))
        with self.assertRaises(GoalNotFoundError):
            self.repository.update(make_goal("missing", "user-1"))

    def test_user_isolation(self) -> None:
        """One user's listing never exposes goals that belong to another user."""

        self.repository.create(make_goal("goal-1", "user-1"))
        self.repository.create(make_goal("goal-2", "user-2"))

        self.assertEqual([goal.id for goal in self.repository.list_by_user("user-1")], ["goal-1"])
        self.assertEqual([goal.id for goal in self.repository.list_by_user("user-2")], ["goal-2"])


if __name__ == "__main__":
    unittest.main()

