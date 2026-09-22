"""Unit tests for V1 Goal2Action domain models."""

from datetime import UTC, datetime, timedelta, timezone
import unittest

from app.models import (
    Evidence,
    EvidenceStatus,
    EvidenceType,
    Goal,
    GoalStatus,
    Plan,
    PlanStatus,
    Priority,
    ProgressEvent,
    ProgressEventType,
    RiskAssessment,
    RiskLevel,
    Task,
    TaskStatus,
    UserContext,
)


NOW = datetime(2026, 9, 22, 12, 0, tzinfo=UTC)


class DomainModelCreationTests(unittest.TestCase):
    """Creation tests cover each V1 model using valid strongly typed values."""

    def test_goal_creation(self) -> None:
        goal = Goal("goal-1", "user-1", "Pass calculus", status=GoalStatus.ACTIVE, priority=Priority.HIGH, target_date=NOW)
        self.assertEqual(goal.status, GoalStatus.ACTIVE)

    def test_task_creation(self) -> None:
        task = Task("task-1", "goal-1", "plan-1", "Review derivatives", estimate_minutes=45, due_at=NOW)
        self.assertEqual(task.status, TaskStatus.PROPOSED)

    def test_plan_creation(self) -> None:
        plan = Plan("plan-2", "goal-1", 2, status=PlanStatus.ACTIVE, predecessor_plan_id="plan-1", schedule_window=(NOW, NOW + timedelta(days=1)))
        self.assertEqual(plan.revision, 2)

    def test_progress_event_is_immutable(self) -> None:
        event = ProgressEvent("event-1", "goal-1", ProgressEventType.EFFORT_LOGGED, "user-1", actual_minutes=30)
        with self.assertRaises(AttributeError):
            event.note = "changed"  # type: ignore[misc]

    def test_evidence_creation(self) -> None:
        evidence = Evidence("evidence-1", "goal-1", EvidenceType.USER_NOTE, "Finished chapter", "note://1", "user-1", status=EvidenceStatus.VERIFIED)
        self.assertEqual(evidence.status, EvidenceStatus.VERIFIED)

    def test_user_context_creation(self) -> None:
        from datetime import time

        context = UserContext("user-1", "Asia/Kolkata", [(time(9), time(11))], {"daily_minutes": 120})
        self.assertEqual(context.workload_limits["daily_minutes"], 120)

    def test_risk_assessment_creation(self) -> None:
        risk = RiskAssessment("risk-1", "goal-1", RiskLevel.HIGH, "Limited availability", 300, 120, "Reduce scope")
        self.assertEqual(risk.level, RiskLevel.HIGH)


class DomainModelValidationTests(unittest.TestCase):
    """Validation tests cover enum, temporal, and numeric invariants."""

    def test_rejects_raw_enum_value(self) -> None:
        with self.assertRaises(ValueError):
            Goal("goal-1", "user-1", "Pass calculus", status="active")  # type: ignore[arg-type]

    def test_rejects_non_utc_datetime(self) -> None:
        non_utc = datetime(2026, 9, 22, 12, 0, tzinfo=timezone(timedelta(hours=5)))
        with self.assertRaises(ValueError):
            Task("task-1", "goal-1", "plan-1", "Review", due_at=non_utc)

    def test_rejects_invalid_schedule_window(self) -> None:
        with self.assertRaises(ValueError):
            Plan("plan-1", "goal-1", 1, schedule_window=(NOW, NOW))

    def test_rejects_invalid_completion_percentage(self) -> None:
        with self.assertRaises(ValueError):
            ProgressEvent("event-1", "goal-1", ProgressEventType.STATUS_UPDATE, "user-1", completion_percent=101)

    def test_rejects_negative_capacity(self) -> None:
        with self.assertRaises(ValueError):
            RiskAssessment("risk-1", "goal-1", RiskLevel.LOW, "On track", -1, 60, "Continue")


if __name__ == "__main__":
    unittest.main()
