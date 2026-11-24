from __future__ import annotations

import json
import math
import re
from typing import Any


class WorldMaterializationError(ValueError):
    pass


_ALLOWED_PARTS = {"Part", "SpawnLocation", "WedgePart", "TrussPart"}
_ALLOWED_MATERIALS = {
    "Plastic", "Wood", "Slate", "Concrete", "Grass", "Metal", "DiamondPlate",
    "Fabric", "SmoothPlastic", "Brick", "Sand", "Ice", "Glass", "Rock",
    "Ground", "Mud", "Snow", "WoodPlanks", "Cobblestone",
}


def _number(value: Any, field: str, minimum: float, maximum: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise WorldMaterializationError(f"{field} must be a number.")
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise WorldMaterializationError(f"{field} must be between {minimum} and {maximum}.")
    return float(value)


def _vector(value: Any, field: str, minimum: float, maximum: float,
            positive: bool = False) -> tuple[float, float, float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise WorldMaterializationError(f"{field} must contain exactly three numbers.")
    values = tuple(_number(v, field, minimum, maximum) for v in value)
    if positive and any(v <= 0 for v in values):
        raise WorldMaterializationError(f"{field} dimensions must be positive.")
    return values


def _name(value: Any, fallback: str) -> str:
    if not isinstance(value, str):
        value = fallback
    clean = re.sub(r"[^A-Za-z0-9_ -]", "", value).strip()[:64]
    return clean or fallback


def _lua(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, allow_nan=False)


def build_world_materialization_script(
    name: str,
    objects: list[dict[str, Any]],
    terrain_blocks: list[dict[str, Any]] | None = None,
    lighting: dict[str, Any] | None = None,
    save_place: bool = False,
) -> dict:
    """Create a bounded, injection-safe Luau scene builder for Open Cloud execution."""
    if not isinstance(objects, list) or len(objects) > 300:
        raise WorldMaterializationError("Provide at most 300 world objects.")
    terrain_blocks = [] if terrain_blocks is None else terrain_blocks
    if not isinstance(terrain_blocks, list) or len(terrain_blocks) > 100:
        raise WorldMaterializationError("Provide at most 100 terrain blocks.")
    if not isinstance(save_place, bool):
        raise WorldMaterializationError("save_place must be boolean.")

    world_name = _name(name, "APOLO_GeneratedWorld")
    normalized_objects = []
    for index, item in enumerate(objects):
        if not isinstance(item, dict):
            raise WorldMaterializationError(f"Object #{index + 1} must be an object.")
        class_name = item.get("class_name", "Part")
        if not isinstance(class_name, str) or class_name not in _ALLOWED_PARTS:
            raise WorldMaterializationError(f"Unsupported Roblox part class: {class_name!r}")
        material = item.get("material", "Plastic")
        if not isinstance(material, str) or material not in _ALLOWED_MATERIALS:
            raise WorldMaterializationError(f"Unsupported material: {material!r}")
        color = item.get("color", "#808080")
        if not isinstance(color, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
            raise WorldMaterializationError(f"Object #{index + 1} color must be #RRGGBB.")
        position = _vector(item.get("position", [0, 5, 0]), "position", -100000, 100000)
        size = _vector(item.get("size", [4, 1, 4]), "size", 0.01, 100000, positive=True)
        rotation = _vector(item.get("rotation", [0, 0, 0]), "rotation", -360, 360)
        transparency = _number(item.get("transparency", 0), "transparency", 0, 1)
        anchored = item.get("anchored", True)
        can_collide = item.get("can_collide", True)
        if not isinstance(anchored, bool) or not isinstance(can_collide, bool):
            raise WorldMaterializationError("anchored and can_collide must be booleans.")
        normalized_objects.append({
            "name": _name(item.get("name"), f"Object_{index + 1}"),
            "group": _name(item.get("group", ""), ""),
            "class_name": class_name,
            "material": material,
            "position": position,
            "size": size,
            "rotation": rotation,
            "color": color,
            "transparency": transparency,
            "anchored": anchored,
            "can_collide": can_collide,
        })

    normalized_terrain = []
    for index, item in enumerate(terrain_blocks):
        if not isinstance(item, dict):
            raise WorldMaterializationError(f"Terrain block #{index + 1} must be an object.")
        material = item.get("material", "Grass")
        if not isinstance(material, str) or material not in _ALLOWED_MATERIALS:
            raise WorldMaterializationError(f"Unsupported terrain material: {material!r}")
        normalized_terrain.append({
            "position": _vector(item.get("position", [0, 0, 0]), "terrain position", -100000, 100000),
            "size": _vector(item.get("size", [16, 8, 16]), "terrain size", 0.01, 100000, positive=True),
            "material": material,
        })

    lighting = {} if lighting is None else lighting
    if not isinstance(lighting, dict):
        raise WorldMaterializationError("lighting must be an object.")
    clock_time = _number(lighting.get("clock_time", 14), "clock_time", 0, 24)
    brightness = _number(lighting.get("brightness", 2), "brightness", 0, 10)
    global_shadows = lighting.get("global_shadows", True)
    if not isinstance(global_shadows, bool):
        raise WorldMaterializationError("global_shadows must be boolean.")
    ambient = lighting.get("ambient", "#808080")
    outdoor = lighting.get("outdoor_ambient", "#808080")
    for field, value in (("ambient", ambient), ("outdoor_ambient", outdoor)):
        if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            raise WorldMaterializationError(f"{field} must be #RRGGBB.")

    lines = [
        "-- Generated by APOLO. This script modifies the selected Roblox place.",
        "local Workspace = game:GetService('Workspace')",
        "local Lighting = game:GetService('Lighting')",
        "local Terrain = Workspace:FindFirstChildOfClass('Terrain')",
        f"local worldName = {_lua(world_name)}",
        "if Workspace:FindFirstChild(worldName) then error('A world with this name already exists; choose another name.') end",
        "local root = Instance.new('Model')",
        "root.Name = worldName",
        "root.Parent = Workspace",
        "local groups = {}",
        "local function getGroup(name)",
        "    if name == '' then return root end",
        "    if not groups[name] then",
        "        local model = Instance.new('Model')",
        "        model.Name = name",
        "        model.Parent = root",
        "        groups[name] = model",
        "    end",
        "    return groups[name]",
        "end",
        f"Lighting.ClockTime = {clock_time}",
        f"Lighting.Brightness = {brightness}",
        f"Lighting.GlobalShadows = {str(global_shadows).lower()}",
    ]
    for property, value in (("Ambient", ambient), ("OutdoorAmbient", outdoor)):
        rgb = [int(value[i:i + 2], 16) for i in (1, 3, 5)]
        lines.append(
            f"Lighting.{property} = Color3.fromRGB({rgb[0]}, {rgb[1]}, {rgb[2]})"
        )

    for item in normalized_objects:
        px, py, pz = item["position"]
        sx, sy, sz = item["size"]
        rx, ry, rz = item["rotation"]
        rgb = [int(item["color"][i:i + 2], 16) for i in (1, 3, 5)]
        lines.extend([
            f"local part = Instance.new({_lua(item['class_name'])})",
            f"part.Name = {_lua(item['name'])}",
            f"part.Size = Vector3.new({sx}, {sy}, {sz})",
            f"part.CFrame = CFrame.new({px}, {py}, {pz}) * CFrame.Angles(math.rad({rx}), math.rad({ry}), math.rad({rz}))",
            f"part.Color = Color3.fromRGB({rgb[0]}, {rgb[1]}, {rgb[2]})",
            f"part.Material = Enum.Material.{item['material']}",
            f"part.Anchored = {str(item['anchored']).lower()}",
            f"part.CanCollide = {str(item['can_collide']).lower()}",
            f"part.Transparency = {item['transparency']}",
            f"part.Parent = getGroup({_lua(item['group'])})",
        ])

    for item in normalized_terrain:
        px, py, pz = item["position"]
        sx, sy, sz = item["size"]
        lines.append(
            f"Terrain:FillBlock(CFrame.new({px}, {py}, {pz}), "
            f"Vector3.new({sx}, {sy}, {sz}), Enum.Material.{item['material']})"
        )

    lines.extend([
        f"local saveAttempted = {str(save_place).lower()}",
        "local saved = false",
        "local saveError = nil",
        "if saveAttempted then",
        "    local ok, err = pcall(function()",
        "        game:GetService('AssetService'):SavePlaceAsync({PlaceId = game.PlaceId, SaveWithoutPublish = true})",
        "    end)",
        "    saved = ok",
        "    if not ok then saveError = tostring(err) end",
        "end",
        (f"return {{ success = true, world = worldName, objects = {len(normalized_objects)}, "
         f"terrainBlocks = {len(normalized_terrain)}, saveAttempted = saveAttempted, "
         "saved = saved, saveError = saveError }"),
    ])
    script = "\n".join(lines)
    if len(script.encode("utf-8")) > 4 * 1024 * 1024:
        raise WorldMaterializationError("Generated world script exceeds Roblox's 4 MiB limit.")
    return {
        "script": script,
        "world_name": world_name,
        "object_count": len(normalized_objects),
        "terrain_block_count": len(normalized_terrain),
        "save_place_requested": save_place,
    }
