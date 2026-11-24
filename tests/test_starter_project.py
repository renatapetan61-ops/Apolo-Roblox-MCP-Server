import json
from pathlib import Path


def test_starter_game_rojo_project_references_existing_sources():
    root = Path(__file__).parents[1]
    project_path = root / "examples/starter-game/default.project.json"
    project = json.loads(project_path.read_text(encoding="utf-8"))
    assert project["tree"]["$className"] == "DataModel"
    assert (project_path.parent / "src/ReplicatedStorage/GameConfig.module.luau").is_file()
    assert (project_path.parent / "src/ServerScriptService/Main.server.luau").is_file()
    assert (project_path.parent / "src/StarterPlayer/StarterPlayerScripts/Main.client.luau").is_file()
