from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_ALLOWED_PARTS = {"Part", "SpawnLocation", "Model", "Folder", "WedgePart", "TrussPart"}


def build_world_manifest(root: Path, project: str, name: str, description: str,
                         theme: str, size: str, objects: list[dict[str, Any]]) -> dict:
    base = (root / project).resolve()
    if root.resolve() not in base.parents or not base.is_dir():
        raise ValueError("Project must be an existing directory inside the workspace.")
    clean = []
    for index, obj in enumerate(objects):
        if not isinstance(obj, dict):
            raise ValueError(f"Object {index} must be an object.")
        kind = str(obj.get("class_name", "Part"))
        if kind not in _ALLOWED_PARTS:
            raise ValueError(f"Unsupported class_name: {kind}")
        position = obj.get("position", [0, 5, 0])
        dimensions = obj.get("size", [4, 1, 4])
        if (not isinstance(position, list) or len(position) != 3
                or not all(isinstance(v, (int, float)) for v in position)):
            raise ValueError(f"Object {index} position must contain three numbers.")
        if (not isinstance(dimensions, list) or len(dimensions) != 3
                or not all(isinstance(v, (int, float)) and v > 0 for v in dimensions)):
            raise ValueError(f"Object {index} size must contain three positive numbers.")
        clean.append({
            "name": re.sub(r"[^A-Za-z0-9_ ]", "", str(obj.get("name", f"Object{index+1}")))[:64],
            "class_name": kind, "position": position, "size": dimensions,
            "color": str(obj.get("color", "#808080"))[:16],
            "anchored": bool(obj.get("anchored", True)),
            "material": str(obj.get("material", "Plastic"))[:32],
        })
    manifest = {
        "schema_version": 1, "name": name[:120], "description": description[:1000],
        "theme": theme[:80], "size": size[:40],
        "coordinate_system": "Roblox studs; XYZ",
        "objects": clean,
        "notes": ["Declarative scene specification; not a compiled .rbxl place file.",
                  "A Rojo plugin/build adapter is required to materialize instances in a place."],
    }
    output = base / "worlds" / "world.manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"path": str(output.relative_to(base)), "object_count": len(clean), "manifest": manifest}
