"""Unit tests for the dependency-injected create-goal tool."""

from datetime import UTC, datetime
from unittest.mock import Mock
import unittest

from app.models import Goal, GoalStatus, Priority
from app.services import GoalAlreadyExistsError, GoalRepository
from app.tools import CreateGoalErrorCode, CreateGoalInput, create_goal


NOW = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)


def valid_input() -> CreateGoalInput:
    """Return a complete valid structured input fixture."""

    return CreateGoalInput(
        id="goal-1",
        user_id="user-1",
        title="Pass calculus",
        description="Prepare for the final exam",
        status=GoalStatus.ACTIVE,
        priority=Priority.HIGH,
        success_criteria=["Score at least 70 percent"],
        target_date=NOW,
        created_at=NOW,
        updated_at=NOW,
        constraints={"daily_minutes": "90"},
        tags={"math"},
        version=1,
    )


class CreateGoalToolTests(unittest.TestCase):
    """Verify model construction, error mapping, and repository interaction."""

    def setUp(self) -> None:
        """Use a repository mock to keep these tool tests storage independent."""

        self.repository = Mock(spec=GoalRepository)

    def test_successful_goal_creation_returns_persisted_goal(self) -> None:
        """A valid input creates and returns the goal supplied by the repository."""

        expected_goal = Goal(
            id="goal-1", user_id="user-1", title="Pass calculus", created_at=NOW, updated_at=NOW
        )
        self.repository.create.return_value = expected_goal

        result = create_goal(self.repository, valid_input())

        self.assertEqual(result.goal, expected_goal)
        self.assertIsNone(result.error_code)

    def test_invalid_goal_data_returns_validation_error_without_persistence(self) -> None:
        """Existing Goal validation rejects invalid structured input before storage."""

        invalid = valid_input()
        invalid.status = "active"  # type: ignore[assignment]

        result = create_goal(self.repository, invalid)

        self.assertIsNone(result.goal)
        self.assertEqual(result.error_code, CreateGoalErrorCode.INVALID_GOAL)
        self.repository.create.assert_not_called()

    def test_duplicate_goal_id_returns_clean_error(self) -> None:
        """Repository duplicate errors become a deterministic structured result."""

        self.repository.create.side_effect = GoalAlreadyExistsError("goal already exists: goal-1")

        result = create_goal(self.repository, valid_input())

        self.assertIsNone(result.goal)
        self.assertEqual(result.error_code, CreateGoalErrorCode.DUPLICATE_GOAL_ID)
        self.assertEqual(result.message, "goal already exists: goal-1")

    def test_repository_receives_constructed_goal_model(self) -> None:
        """The tool invokes only the repository abstraction with a valid Goal."""

        self.repository.create.side_effect = lambda goal: goal

        result = create_goal(self.repository, valid_input())

        self.repository.create.assert_called_once()
        persisted_goal = self.repository.create.call_args.args[0]
        self.assertIsInstance(persisted_goal, Goal)
        self.assertEqual(persisted_goal.id, "goal-1")
        self.assertEqual(persisted_goal.status, GoalStatus.ACTIVE)
        self.assertEqual(result.goal, persisted_goal)


if __name__ == "__main__":
    unittest.main()

