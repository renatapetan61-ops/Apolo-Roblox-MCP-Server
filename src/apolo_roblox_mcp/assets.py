from __future__ import annotations

import hashlib
import json
import mimetypes
import uuid
import zipfile
from pathlib import Path


def _paths(root: Path, project: str) -> tuple[Path, Path]:
    base = (root / project).resolve()
    if root.resolve() not in base.parents or not base.is_dir():
        raise ValueError("Project must be an existing directory inside the workspace.")
    library = base / "assets"
    library.mkdir(exist_ok=True)
    return base, library


def import_asset(root: Path, project: str, source_path: str, category: str, name: str) -> dict:
    source = Path(source_path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source_path)
    if source.stat().st_size > 50 * 1024 * 1024:
        raise ValueError("Asset exceeds the 50 MiB import limit.")
    base, library = _paths(root, project)
    asset_id = uuid.uuid4().hex[:12]
    safe_name = "".join(c for c in name if c.isalnum() or c in "-_ ").strip()[:64] or "asset"
    ext = source.suffix.lower()[:10]
    target = library / f"{asset_id}-{safe_name}{ext}"
    target.write_bytes(source.read_bytes())
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    record = {"asset_id": asset_id, "name": safe_name, "category": category[:40],
              "file": str(target.relative_to(base)), "sha256": digest,
              "bytes": target.stat().st_size,
              "media_type": mimetypes.guess_type(target.name)[0] or "application/octet-stream",
              "origin": "user_import", "roblox_asset_id": None}
    index = library / "index.json"
    records = json.loads(index.read_text()) if index.exists() else []
    records.append(record)
    index.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    return record


def list_assets(root: Path, project: str) -> list[dict]:
    _, library = _paths(root, project)
    index = library / "index.json"
    return json.loads(index.read_text()) if index.exists() else []


def export_assets(root: Path, project: str) -> dict:
    base, library = _paths(root, project)
    records = list_assets(root, project)
    output = base / "exports"
    output.mkdir(exist_ok=True)
    archive = output / f"assets-{uuid.uuid4().hex[:8]}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
        for record in records:
            path = (base / record["file"]).resolve()
            if library not in path.parents or not path.is_file():
                raise ValueError("Asset catalog contains an invalid file reference.")
            zf.write(path, record["file"])
        if (library / "index.json").exists():
            zf.write(library / "index.json", "assets/index.json")
    return {"archive": str(archive), "asset_count": len(records),
            "sha256": hashlib.sha256(archive.read_bytes()).hexdigest()}
