from __future__ import annotations

import json
import re
from pathlib import Path


def create_ui_spec(root: Path, project: str, screen_name: str, purpose: str,
                   palette: dict, components: list[dict]) -> dict:
    base = (root / project).resolve()
    if root.resolve() not in base.parents or not base.is_dir():
        raise ValueError("Project must be an existing directory inside the workspace.")
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "-", screen_name).strip("-").lower() or "screen"
    tokens = {}
    for key, value in palette.items():
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", str(value)):
            raise ValueError(f"Palette value for {key} must be #RRGGBB.")
        tokens[str(key)[:40]] = value
    allowed = {"Frame", "TextLabel", "TextButton", "ImageLabel", "ImageButton",
               "ScrollingFrame", "UICorner", "UIStroke", "UIPadding", "UIListLayout"}
    normalized = []
    for i, item in enumerate(components):
        cls = str(item.get("class_name", "Frame"))
        if cls not in allowed:
            raise ValueError(f"Unsupported UI class: {cls}")
        normalized.append({
            "name": re.sub(r"[^A-Za-z0-9_]", "", str(item.get("name", f"Component{i+1}")))[:64],
            "class_name": cls, "text": str(item.get("text", ""))[:300],
            "size": item.get("size", {"scale_x": 1, "scale_y": 1}),
            "position": item.get("position", {"scale_x": 0, "scale_y": 0}),
            "background": item.get("background", tokens.get("surface", "#202020")),
            "corner_radius": max(0, min(48, int(item.get("corner_radius", 8)))),
        })
    spec = {"schema_version": 1, "screen": safe_name, "purpose": purpose[:500],
            "palette": tokens, "components": normalized,
            "notes": ["Design specification only; pair with generated Luau to create a functional GUI."]}
    output = base / "ui" / f"{safe_name}.ui.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return {"path": str(output.relative_to(base)), "component_count": len(normalized), "spec": spec}
