from pathlib import Path

import pytest

from apolo_roblox_mcp.workspace import create_project, list_files, safe_path, write_text


def test_create_and_write_project(tmp_path: Path):
    created = create_project(tmp_path, "My Roblox Game", "A test game")
    assert created["project"] == "my-roblox-game"
    write_text(tmp_path, created["project"], "src/server/Main.server.lua", "print('hello')")
    files = list_files(tmp_path, created["project"])
    assert "default.project.json" in files
    assert "src/server/Main.server.lua" in files


def test_reject_path_escape(tmp_path: Path):
    with pytest.raises(ValueError):
        safe_path(tmp_path, "../outside")
