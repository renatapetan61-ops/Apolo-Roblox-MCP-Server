from pathlib import Path

import pytest

from apolo_roblox_mcp.agent_runtime import AgentOrchestrator, AgentRunError


def test_agent_run_persists_dependencies_and_handoffs(tmp_path: Path):
    database = tmp_path / ".apolo" / "agents.sqlite3"
    orchestrator = AgentOrchestrator(database)
    created = orchestrator.create_run(
        "Build a cooperative forest adventure",
        "adventure",
        "Roblox mobile",
        ["No paid assets without approval"],
    )
    assert created["status"] == "pending"
    assert created["task_counts"]["pending"] == 8

    architect = orchestrator.claim_task("architect-1", ["architect"])
    assert architect["role"] == "architect"
    architect_id = architect["task_id"]
    run_id = created["run_id"]
    orchestrator.complete_task(
        run_id, architect_id, "architect-1",
        {"game_loop": "Explore, gather, build", "world": "Forest hub"},
    )

    luau = orchestrator.claim_task("luau-1", ["luau_engineer"])
    assert luau is not None
    assert luau["agent_context"]["dependency_outputs"][architect_id]["game_loop"] == "Explore, gather, build"

    # A different worker cannot steal or complete a task it does not own.
    with pytest.raises(AgentRunError):
        orchestrator.complete_task(run_id, luau["task_id"], "other-agent", {"files": []})

    orchestrator.complete_task(run_id, luau["task_id"], "luau-1", {"files": ["Main.server.lua"]})
    restarted = AgentOrchestrator(database)
    state = restarted.get_run(run_id)
    assert state["task_counts"]["completed"] == 2
    assert state["task_counts"]["pending"] == 6


def test_agent_task_roles_are_validated(tmp_path: Path):
    orchestrator = AgentOrchestrator(tmp_path / "agents.sqlite3")
    orchestrator.create_run("A game", "adventure", "Roblox")
    with pytest.raises(AgentRunError):
        orchestrator.claim_task("worker-1", ["admin"])


def test_agent_result_must_be_json_and_small(tmp_path: Path):
    orchestrator = AgentOrchestrator(tmp_path / "agents.sqlite3")
    run = orchestrator.create_run("A game", "adventure", "Roblox")
    task = orchestrator.claim_task("architect-1", ["architect"])
    with pytest.raises(AgentRunError):
        orchestrator.complete_task(run["run_id"], task["task_id"], "architect-1", {"bad": object()})
