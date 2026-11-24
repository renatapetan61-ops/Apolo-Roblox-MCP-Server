from __future__ import annotations

from typing import Any


def plan_game(brief: str, genre: str, target: str, constraints: list[str]) -> dict[str, Any]:
    if len(brief.strip()) < 20:
        raise ValueError("Provide a game brief of at least 20 characters.")
    tasks = [
        {"id": "design", "role": "game_designer", "goal": "Turn the brief into a game design document and acceptance criteria.", "depends_on": []},
        {"id": "world", "role": "world_builder", "goal": "Create world layout, regions, spawn points and environment manifest.", "depends_on": ["design"]},
        {"id": "systems", "role": "gameplay_engineer", "goal": "Implement server-authoritative gameplay systems in Luau.", "depends_on": ["design"]},
        {"id": "ui", "role": "ui_designer", "goal": "Create UI specifications and corresponding client/server behavior.", "depends_on": ["design"]},
        {"id": "assets", "role": "asset_artist", "goal": "List required art, audio, model and animation assets with provider/licensing requirements.", "depends_on": ["design"]},
        {"id": "qa", "role": "qa_engineer", "goal": "Validate project structure, Luau, security boundaries and test evidence.", "depends_on": ["world", "systems", "ui", "assets"]},
        {"id": "release", "role": "release_manager", "goal": "Package release candidate and prepare manual or approval-gated publication.", "depends_on": ["qa"]},
    ]
    return {"brief": brief, "genre": genre, "target": target, "constraints": constraints,
            "tasks": tasks,
            "execution_model": "task graph for an MCP client/AI agent; this server does not claim to run autonomous agents in background.",
            "approval_required_for": ["external asset purchases", "public asset uploads", "Roblox place publication"]}
