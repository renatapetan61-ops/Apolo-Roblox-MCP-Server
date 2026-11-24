import pytest

from apolo_roblox_mcp.world_runtime import (
    WorldMaterializationError,
    build_world_materialization_script,
)


def test_builds_real_world_materialization_script():
    result = build_world_materialization_script(
        "ForestWorld",
        [{
            "name": "Ground",
            "class_name": "Part",
            "position": [0, 0, 0],
            "size": [100, 4, 100],
            "material": "Grass",
            "group": "TerrainProps",
        }],
        terrain_blocks=[{"position": [0, -4, 0], "size": [120, 8, 120], "material": "Ground"}],
        lighting={"clock_time": 18, "brightness": 2.5},
        save_place=False,
    )
    script = result["script"]
    assert "Instance.new" in script
    assert "Workspace" in script
    assert "Terrain:FillBlock" in script
    assert "Lighting.ClockTime = 18.0" in script
    assert "SaveWithoutPublish = true" in script
    assert result["object_count"] == 1
    assert result["terrain_block_count"] == 1
    assert result["save_place_requested"] is False


def test_rejects_injected_names_and_invalid_materials():
    result = build_world_materialization_script(
        "Map; error('bad')",
        [{"name": "ok", "material": "NotARealMaterial"}],
    )
    assert result["world_name"] == "Map errorbad"
    with pytest.raises(WorldMaterializationError):
        build_world_materialization_script("Map", [{"material": "Nope"}])


def test_rejects_invalid_geometry():
    with pytest.raises(WorldMaterializationError):
        build_world_materialization_script("Map", [{"size": [0, 1, 1]}])
