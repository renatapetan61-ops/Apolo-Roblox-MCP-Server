from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any


class AgentRunError(ValueError):
    pass


_AGENT_ID = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
_TASKS = (
    ("architect", "Game architecture", "Define the game loop, progression, systems, scene plan, and technical boundaries."),
    ("luau_engineer", "Luau engineering", "Implement server/client Luau modules, data contracts, remotes, and gameplay systems."),
    ("world_builder", "World construction", "Create the 3D scene plan and materializable world specification with terrain, structures, and lighting."),
    ("visual_artist", "Visual assets", "Prepare icon, thumbnail, UI, texture, and model asset briefs; use configured providers only for real generation."),
    ("audio_designer", "Audio and animation", "Prepare music, sound effect, and animation requirements and provider-ready asset specifications."),
    ("integrator", "Game integration", "Integrate completed Luau, world, visual, and audio deliverables into a coherent project."),
    ("qa_engineer", "Quality assurance", "Create and run automated game checks, review logs, and report blockers and regressions."),
    ("release_manager", "Release preparation", "Prepare build artifacts, hashes, approval checklist, and manual or protected publishing handoff."),
)


class AgentOrchestrator:
    """Persistent role-based task DAG for AI workers connected through MCP."""

    def __init__(self, database: Path, lease_seconds: int = 900, max_attempts: int = 3):
        self.database = Path(database)
        self.lease_seconds = max(30, min(lease_seconds, 3600))
        self.max_attempts = max(1, min(max_attempts, 10))
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with self._session() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    brief TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    target TEXT NOT NULL,
                    constraints_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(run_id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    title TEXT NOT NULL,
                    instructions TEXT NOT NULL,
                    depends_on_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    max_attempts INTEGER NOT NULL,
                    owner TEXT,
                    lease_until REAL,
                    output_json TEXT,
                    error TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_agent_tasks_ready
                    ON tasks(run_id, status, created_at);
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database, timeout=15)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    @contextmanager
    def _session(self):
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
    def _agent_id(value: str) -> str:
        if not isinstance(value, str) or not _AGENT_ID.fullmatch(value):
            raise AgentRunError("agent_id must contain 1-64 letters, numbers, dots, underscores or hyphens.")
        return value

    def create_run(self, brief: str, genre: str, target: str,
                   constraints: list[str] | None = None) -> dict:
        if not isinstance(brief, str) or not brief.strip() or len(brief) > 12000:
            raise AgentRunError("brief must contain 1-12000 characters.")
        if not isinstance(genre, str) or not genre.strip() or len(genre) > 80:
            raise AgentRunError("genre must contain 1-80 characters.")
        if not isinstance(target, str) or not target.strip() or len(target) > 120:
            raise AgentRunError("target must contain 1-120 characters.")
        constraints = [] if constraints is None else constraints
        if not isinstance(constraints, list) or len(constraints) > 50:
            raise AgentRunError("constraints must be a list with at most 50 entries.")
        if any(not isinstance(item, str) or len(item) > 500 for item in constraints):
            raise AgentRunError("Each constraint must be text with at most 500 characters.")

        run_id = uuid.uuid4().hex
        now = time.time()
        task_ids = {role: uuid.uuid4().hex for role, _, _ in _TASKS}
        dependencies = {
            "architect": [],
            "luau_engineer": ["architect"],
            "world_builder": ["architect"],
            "visual_artist": ["architect"],
            "audio_designer": ["architect"],
            "integrator": ["luau_engineer", "world_builder", "visual_artist", "audio_designer"],
            "qa_engineer": ["integrator"],
            "release_manager": ["qa_engineer"],
        }
        with self._session() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?)",
                (run_id, brief.strip(), genre.strip(), target.strip(),
                 json.dumps(constraints), now, now),
            )
            for role, title, instructions in _TASKS:
                dependency_ids = [task_ids[item] for item in dependencies[role]]
                connection.execute(
                    """INSERT INTO tasks
                    (task_id, run_id, role, title, instructions, depends_on_json,
                     status, attempts, max_attempts, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 'pending', 0, ?, ?, ?)""",
                    (task_ids[role], run_id, role, title, instructions,
                     json.dumps(dependency_ids), self.max_attempts, now, now),
                )
        return self.get_run(run_id)

    def claim_task(self, agent_id: str, roles: list[str] | None = None) -> dict | None:
        agent_id = self._agent_id(agent_id)
        allowed_roles = None
        if roles is not None:
            if not isinstance(roles, list) or any(role not in {item[0] for item in _TASKS} for role in roles):
                raise AgentRunError("roles contains an unknown agent role.")
            allowed_roles = set(roles)
        now = time.time()
        with self._session() as connection:
            connection.execute("BEGIN IMMEDIATE")
            expired = connection.execute(
                "SELECT task_id, attempts, max_attempts FROM tasks "
                "WHERE status='running' AND lease_until < ?",
                (now,),
            ).fetchall()
            for task in expired:
                next_status = "pending" if task["attempts"] < task["max_attempts"] else "failed"
                connection.execute(
                    "UPDATE tasks SET status=?, owner=NULL, lease_until=NULL, "
                    "error='Agent lease expired.', updated_at=? WHERE task_id=?",
                    (next_status, now, task["task_id"]),
                )

            candidates = connection.execute(
                "SELECT * FROM tasks WHERE status='pending' ORDER BY created_at, role"
            ).fetchall()
            for task in candidates:
                if allowed_roles is not None and task["role"] not in allowed_roles:
                    continue
                dependency_ids = json.loads(task["depends_on_json"])
                if dependency_ids:
                    placeholders = ",".join("?" for _ in dependency_ids)
                    dependency_rows = connection.execute(
                        f"SELECT task_id, status, output_json FROM tasks WHERE task_id IN ({placeholders})",
                        dependency_ids,
                    ).fetchall()
                    if len(dependency_rows) != len(dependency_ids) or any(
                        row["status"] != "completed" for row in dependency_rows
                    ):
                        continue
                else:
                    dependency_rows = []

                lease_until = now + self.lease_seconds
                connection.execute(
                    "UPDATE tasks SET status='running', owner=?, lease_until=?, "
                    "attempts=attempts+1, updated_at=? WHERE task_id=? AND status='pending'",
                    (agent_id, lease_until, now, task["task_id"]),
                )
                claimed = connection.execute(
                    "SELECT * FROM tasks WHERE task_id=?", (task["task_id"],)
                ).fetchone()
                run = connection.execute(
                    "SELECT brief, genre, target, constraints_json FROM runs WHERE run_id=?",
                    (task["run_id"],),
                ).fetchone()
                return {
                    **self._task_dict(claimed),
                    "lease_until": lease_until,
                    "agent_context": {
                        "brief": run["brief"],
                        "genre": run["genre"],
                        "target": run["target"],
                        "constraints": json.loads(run["constraints_json"]),
                        "dependency_outputs": {
                            row["task_id"]: json.loads(row["output_json"])
                            for row in dependency_rows if row["output_json"]
                        },
                    },
                }
        return None

    def complete_task(self, run_id: str, task_id: str, agent_id: str,
                      output: dict, success: bool = True) -> dict:
        agent_id = self._agent_id(agent_id)
        if not isinstance(output, dict) or not isinstance(success, bool):
            raise AgentRunError("output must be an object and success must be boolean.")
        try:
            serialized = json.dumps(output, ensure_ascii=False, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise AgentRunError("output must be JSON-serializable and contain no NaN or Infinity.") from exc
        if len(serialized.encode("utf-8")) > 1024 * 1024:
            raise AgentRunError("Agent output exceeds the 1 MiB task-result limit.")

        now = time.time()
        with self._session() as connection:
            connection.execute("BEGIN IMMEDIATE")
            task = connection.execute(
                "SELECT * FROM tasks WHERE task_id=? AND run_id=?",
                (task_id, run_id),
            ).fetchone()
            if task is None:
                raise AgentRunError("Task does not belong to this run.")
            if task["status"] != "running" or task["owner"] != agent_id:
                raise AgentRunError("Only the agent holding the active task lease can complete it.")
            if task["lease_until"] is None or task["lease_until"] < now:
                raise AgentRunError("Task lease expired; claim the task again before submitting results.")

            if success:
                status = "completed"
                error = None
            else:
                status = "pending" if task["attempts"] < task["max_attempts"] else "failed"
                error = str(output.get("error", "Agent reported task failure"))[:2000]
            connection.execute(
                "UPDATE tasks SET status=?, owner=NULL, lease_until=NULL, output_json=?, "
                "error=?, updated_at=? WHERE task_id=?",
                (status, serialized, error, now, task_id),
            )
            connection.execute("UPDATE runs SET updated_at=? WHERE run_id=?", (now, run_id))
        return self.get_run(run_id)

    def get_run(self, run_id: str) -> dict:
        with self._session() as connection:
            run = connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if run is None:
                raise AgentRunError("Unknown agent run ID.")
            tasks = connection.execute(
                "SELECT * FROM tasks WHERE run_id=? ORDER BY created_at, role", (run_id,)
            ).fetchall()
        task_dicts = [self._task_dict(task) for task in tasks]
        statuses = [task["status"] for task in task_dicts]
        if statuses and all(status == "completed" for status in statuses):
            status = "completed"
        elif "failed" in statuses:
            status = "blocked"
        elif "running" in statuses:
            status = "running"
        else:
            status = "pending"
        return {
            "run_id": run["run_id"],
            "status": status,
            "brief": run["brief"],
            "genre": run["genre"],
            "target": run["target"],
            "constraints": json.loads(run["constraints_json"]),
            "created_at": run["created_at"],
            "updated_at": run["updated_at"],
            "task_counts": {state: statuses.count(state) for state in
                            ("pending", "running", "completed", "failed")},
            "tasks": task_dicts,
        }

    @staticmethod
    def _task_dict(task: sqlite3.Row) -> dict:
        return {
            "task_id": task["task_id"],
            "run_id": task["run_id"],
            "role": task["role"],
            "title": task["title"],
            "instructions": task["instructions"],
            "depends_on": json.loads(task["depends_on_json"]),
            "status": task["status"],
            "attempts": task["attempts"],
            "max_attempts": task["max_attempts"],
            "owner": task["owner"],
            "lease_until": task["lease_until"],
            "output": json.loads(task["output_json"]) if task["output_json"] else None,
            "error": task["error"],
        }
