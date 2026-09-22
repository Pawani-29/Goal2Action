"""Standard-library SQLite development adapter for the GoalRepository contract."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
import json
from pathlib import Path
import sqlite3

from app.models import Goal, GoalStatus, Priority

from .goal_repository import GoalAlreadyExistsError, GoalNotFoundError, GoalRepository


class SQLiteGoalRepository(GoalRepository):
    """Store validated Goal records in a local SQLite file.

    Connections are short lived so independently constructed repository instances
    observe the same on-disk data. The adapter deliberately owns SQL and storage
    conversion while the Goal model remains independent of persistence.
    """

    _CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS goals (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            success_criteria_json TEXT NOT NULL,
            target_date TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            constraints_json TEXT NOT NULL,
            tags_json TEXT NOT NULL,
            version INTEGER NOT NULL
        )
    """

    _COLUMNS = (
        "id, user_id, title, description, status, priority, success_criteria_json, "
        "target_date, created_at, updated_at, constraints_json, tags_json, version"
    )

    def __init__(self, database_path: str | Path) -> None:
        """Open (or initialize) the SQLite database at ``database_path``."""

        self._database_path = str(database_path)
        with self._connection() as connection:
            connection.execute(self._CREATE_TABLE_SQL)

    def create(self, goal: Goal) -> Goal:
        """Persist a new validated goal, rejecting a duplicate ID."""

        stored_goal = self._validated_copy(goal)
        try:
            with self._connection() as connection:
                connection.execute(
                    f"INSERT INTO goals ({self._COLUMNS}) VALUES ({', '.join('?' for _ in range(13))})",
                    self._goal_values(stored_goal),
                )
        except sqlite3.IntegrityError as error:
            raise GoalAlreadyExistsError(f"goal already exists: {goal.id}") from error
        return stored_goal

    def get_by_id(self, goal_id: str) -> Goal | None:
        """Read and validate a goal by ID, returning ``None`` when absent."""

        with self._connection() as connection:
            row = connection.execute(
                f"SELECT {self._COLUMNS} FROM goals WHERE id = ?", (goal_id,)
            ).fetchone()
        return self._goal_from_row(row) if row is not None else None

    def list_by_user(self, user_id: str) -> list[Goal]:
        """Read and validate all goals for one user in creation order."""

        with self._connection() as connection:
            rows = connection.execute(
                f"SELECT {self._COLUMNS} FROM goals WHERE user_id = ? ORDER BY created_at, id",
                (user_id,),
            ).fetchall()
        return [self._goal_from_row(row) for row in rows]

    def update(self, goal: Goal) -> Goal:
        """Replace a stored goal after reapplying the domain model validation."""

        stored_goal = self._validated_copy(goal)
        assignments = ", ".join(f"{column} = ?" for column in self._COLUMNS.split(", ")[1:])
        with self._connection() as connection:
            cursor = connection.execute(
                f"UPDATE goals SET {assignments} WHERE id = ?",
                (*self._goal_values(stored_goal)[1:], stored_goal.id),
            )
        if cursor.rowcount == 0:
            raise GoalNotFoundError(f"goal not found: {stored_goal.id}")
        return stored_goal

    def delete(self, goal_id: str) -> bool:
        """Delete a goal by ID and report whether a row was removed."""

        with self._connection() as connection:
            cursor = connection.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        return cursor.rowcount > 0

    def _connect(self) -> sqlite3.Connection:
        """Create a row-addressable connection with transactional context support."""

        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _connection(self):
        """Yield a transaction and always close its underlying SQLite connection."""

        connection = self._connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _validated_copy(goal: Goal) -> Goal:
        """Reconstruct a Goal so persistence never bypasses its invariants."""

        return Goal(
            id=goal.id,
            user_id=goal.user_id,
            title=goal.title,
            description=goal.description,
            status=goal.status,
            priority=goal.priority,
            success_criteria=list(goal.success_criteria),
            target_date=goal.target_date,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
            constraints=dict(goal.constraints),
            tags=set(goal.tags),
            version=goal.version,
        )

    @staticmethod
    def _goal_values(goal: Goal) -> tuple[object, ...]:
        """Serialize a validated Goal into SQLite-compatible scalar values."""

        return (
            goal.id,
            goal.user_id,
            goal.title,
            goal.description,
            goal.status.value,
            goal.priority.value,
            json.dumps(goal.success_criteria),
            goal.target_date.isoformat() if goal.target_date else None,
            goal.created_at.isoformat(),
            goal.updated_at.isoformat(),
            json.dumps(goal.constraints),
            json.dumps(sorted(goal.tags)),
            goal.version,
        )

    @staticmethod
    def _goal_from_row(row: sqlite3.Row) -> Goal:
        """Deserialize a row into Goal, allowing its existing validation to run."""

        target_date = datetime.fromisoformat(row["target_date"]) if row["target_date"] else None
        return Goal(
            id=row["id"],
            user_id=row["user_id"],
            title=row["title"],
            description=row["description"],
            status=GoalStatus(row["status"]),
            priority=Priority(row["priority"]),
            success_criteria=json.loads(row["success_criteria_json"]),
            target_date=target_date,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            constraints=json.loads(row["constraints_json"]),
            tags=set(json.loads(row["tags_json"])),
            version=row["version"],
        )
