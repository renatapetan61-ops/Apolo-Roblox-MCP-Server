from pathlib import Path

import pytest

from apolo_roblox_mcp.assets import export_assets, import_asset, list_assets
from apolo_roblox_mcp.luau import validate_luau
from apolo_roblox_mcp.ui import create_ui_spec
from apolo_roblox_mcp.workspace import create_project
from apolo_roblox_mcp.worlds import build_world_manifest


def project(tmp_path: Path) -> str:
    return create_project(tmp_path, "Game", "A test game")["project"]


def test_world_manifest(tmp_path: Path):
    slug = project(tmp_path)
    result = build_world_manifest(tmp_path, slug, "Forest", "Starter forest", "fantasy", "small",
                                  [{"name": "Ground", "size": [100, 2, 100]}])
    assert result["object_count"] == 1
    assert (tmp_path / slug / "src/server/GeneratedWorld.server.lua").is_file()
    assert (tmp_path / slug / result["path"]).is_file()


def test_world_rejects_invalid_part(tmp_path: Path):
    slug = project(tmp_path)
    with pytest.raises(ValueError):
        build_world_manifest(tmp_path, slug, "Bad", "", "", "",
                             [{"class_name": "Script", "size": [1, 1, 1]}])


def test_ui_spec(tmp_path: Path):
    slug = project(tmp_path)
    result = create_ui_spec(tmp_path, slug, "Main Menu", "Main menu",
                            {"surface": "#202020"}, [{"class_name": "TextButton", "text": "Play"}])
    assert result["component_count"] == 1
    assert (tmp_path / slug / "src/client/main-menu.client.lua").is_file()


def test_asset_import_and_export(tmp_path: Path):
    slug = project(tmp_path)
    source = tmp_path / "source.png"
    source.write_bytes(b"fake-png-for-test")
    item = import_asset(tmp_path, slug, str(source), "icon", "Game Icon")
    assert len(list_assets(tmp_path, slug)) == 1
    result = export_assets(tmp_path, slug)
    assert result["asset_count"] == 1
    assert Path(result["archive"]).is_file()
    assert item["sha256"]


def test_luau_validation_reports_missing_tool(tmp_path: Path, monkeypatch):
    slug = project(tmp_path)
    target = tmp_path / slug / "src" / "server" / "Main.server.lua"
    target.write_text("print('hello')")
    monkeypatch.setattr("apolo_roblox_mcp.luau.shutil.which", lambda _: None)
    assert validate_luau(tmp_path, slug, "src/server/Main.server.lua")["status"] == "skipped"
