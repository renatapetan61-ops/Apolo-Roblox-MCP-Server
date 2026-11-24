from apolo_roblox_mcp.test_runner import build_game_test_script, summarize_task
import pytest


def test_builds_safe_game_test_harness():
    script = build_game_test_script([
        {"id": "spawn_exists", "kind": "instance_exists", "path": "Workspace.SpawnLocation"},
        {"id": "spawn_class", "kind": "is_a", "path": "Workspace.SpawnLocation", "class_name": "SpawnLocation"},
        {"id": "spawn_children", "kind": "child_count", "path": "Workspace.SpawnLocation", "expected": 0},
        {"id": "anchored", "kind": "property_equals", "path": "Workspace.SpawnLocation", "property": "Anchored", "expected": True},
        {"id": "zone_tag", "kind": "attribute_equals", "path": "Workspace.SpawnLocation", "attribute": "Zone", "expected": "Lobby"},
    ])
    assert "FindFirstChild" in script
    assert "IsA" in script
    assert "GetAttribute" in script
    assert "success = failed == 0" in script


def test_rejects_unsafe_test_specs():
    with pytest.raises(ValueError):
        build_game_test_script([{"id": "x", "kind": "instance_exists", "path": "Workspace.Parent.Parent"}])
    with pytest.raises(ValueError):
        build_game_test_script([{"id": "x", "kind": "execute_code", "path": "Workspace"}])


def test_summarizes_completed_game_test():
    result = summarize_task({"response": {
        "state": "COMPLETE",
        "output": {"results": [{"success": False, "passed": 2, "failed": 1}]},
    }})
    assert result["outcome"] == "failed"
    assert result["summary"]["failed"] == 1
