from pathlib import Path

from apolo_roblox_mcp.build import build_place
from apolo_roblox_mcp.workspace import create_project


def test_build_reports_missing_rojo(tmp_path: Path, monkeypatch):
    slug = create_project(tmp_path, "Build Test", "test")["project"]
    monkeypatch.setattr("apolo_roblox_mcp.build.shutil.which", lambda _: None)
    result = build_place(tmp_path, slug)
    assert result["status"] == "blocked"
