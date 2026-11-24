from __future__ import annotations

import hashlib
import json
import os
import uuid
import zipfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .config import Settings
from .open_cloud import OpenCloudClient
from .workspace import create_project, list_files, safe_path, write_text

settings = Settings.from_env()
mcp = FastMCP("APOLO Roblox MCP Server")
_selected_mode = settings.default_integration
_publish_candidates: dict[str, dict] = {}

CAPABILITIES = {
    "studio_compat": [
        "project.scaffold", "project.inspect", "luau.write", "luau.validate",
        "world.manifest", "ui.spec", "project.package",
    ],
    "open_cloud": [
        "cloud.place.publish", "cloud.place.metadata", "cloud.asset.operations",
        "cloud.datastores",
    ],
}


def _project_path(project: str) -> Path:
    path = safe_path(settings.workspace, project)
    if not path.is_dir():
        raise FileNotFoundError(f"Project not found: {project}")
    return path


@mcp.tool()
def apolo_server_info() -> dict:
    """Return server version, configured workspace and supported integration modes."""
    from . import __version__
    return {
        "name": "APOLO Roblox MCP Server",
        "version": __version__,
        "workspace": str(settings.workspace),
        "integrations": ["studio_compat", "open_cloud"],
        "selected_integration": _selected_mode,
        "studio_required": False,
    }


@mcp.tool()
def apolo_select_integration(mode: str) -> dict:
    """Select 'studio_compat' for headless Studio-like project workflows or 'open_cloud' for Roblox cloud APIs."""
    global _selected_mode
    if mode not in {"studio_compat", "open_cloud"}:
        raise ValueError("mode must be 'studio_compat' or 'open_cloud'.")
    _selected_mode = mode
    return {"selected_integration": mode, "capabilities": CAPABILITIES[mode]}


@mcp.tool()
def apolo_list_capabilities() -> dict:
    """List capabilities available in each integration; planned capabilities are not implied to be implemented."""
    return {
        "implemented": [
            "server.info", "integration.select", "project.scaffold",
            "project.inspect", "luau.write", "project.package",
            "cloud.place.publish_with_approval",
        ],
        "planned": {
            "studio_compat": ["luau.validate", "world.manifest", "ui.spec", "live.playtest"],
            "open_cloud": ["place.metadata", "asset.operations", "datastores"],
            "assets": ["thumbnail", "icon", "gui", "hud", "avatar", "model3d",
                       "clothing", "music", "sound_effect", "r15_animation", "asset_library"],
        },
        "notes": [
            "Studio compatibility mode works on project files and does not require Roblox Studio.",
            "Live DataModel inspection and Play testing require Studio or a separately configured runtime.",
            "Asset generation requires a configured provider; no provider is bundled by default.",
        ],
    }


@mcp.tool()
def apolo_create_project(name: str, description: str = "") -> dict:
    """Create a Rojo-compatible Roblox project skeleton in the configured workspace."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat before creating a local project.")
    return create_project(settings.workspace, name, description)


@mcp.tool()
def apolo_list_project_files(project: str) -> dict:
    """List files in an APOLO project."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat to inspect local project files.")
    return {"project": project, "files": list_files(settings.workspace, project)}


@mcp.tool()
def apolo_read_project_file(project: str, path: str) -> dict:
    """Read a UTF-8 text file from a project. Binary files are not returned by this tool."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat to read local project files.")
    target = safe_path(_project_path(project), path)
    if not target.is_file():
        raise FileNotFoundError(path)
    return {"path": path, "content": target.read_text(encoding="utf-8")}


@mcp.tool()
def apolo_write_project_file(project: str, path: str, content: str) -> dict:
    """Create or replace a UTF-8 project file. Paths are restricted to the project directory."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat to edit local project files.")
    return write_text(settings.workspace, project, path, content)


@mcp.tool()
def apolo_package_project(project: str) -> dict:
    """Create a deterministic ZIP source package and return its SHA-256 hash."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat before packaging a project.")
    base = _project_path(project)
    output_dir = settings.workspace / "artifacts"
    output_dir.mkdir(exist_ok=True)
    archive = output_dir / f"{project}-{uuid.uuid4().hex[:8]}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in sorted(p for p in base.rglob("*") if p.is_file()):
            zf.write(item, item.relative_to(base))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    return {"artifact": str(archive), "sha256": digest, "bytes": archive.stat().st_size}


@mcp.tool()
def apolo_prepare_publish(artifact_path: str, universe_id: str, place_id: str) -> dict:
    """Prepare an immutable release candidate. This does not publish anything."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before preparing a Roblox cloud release.")
    artifact = Path(artifact_path).expanduser().resolve()
    if not artifact.is_file() or artifact.suffix.lower() not in {".rbxl", ".rbxlx"}:
        raise ValueError("Provide an existing .rbxl or .rbxlx place file.")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    candidate_id = uuid.uuid4().hex
    _publish_candidates[candidate_id] = {
        "path": str(artifact), "sha256": digest,
        "universe_id": universe_id, "place_id": place_id,
    }
    return {
        "candidate_id": candidate_id,
        "sha256": digest,
        "universe_id": universe_id,
        "place_id": place_id,
        "approval_phrase": f"APPROVE ROBLOX RELEASE {candidate_id}",
        "published": False,
        "next_step": "Review target and hash, then pass the exact approval phrase to apolo_publish_approved.",
    }


@mcp.tool()
def apolo_publish_approved(candidate_id: str, approval_phrase: str) -> dict:
    """Publish a prepared place only when the exact release-specific approval phrase is supplied."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before publishing.")
    candidate = _publish_candidates.get(candidate_id)
    if candidate is None:
        raise ValueError("Unknown or expired release candidate.")
    expected = f"APPROVE ROBLOX RELEASE {candidate_id}"
    if approval_phrase != expected:
        raise PermissionError("Approval phrase does not match this release candidate.")
    api_key = settings.roblox_api_key
    if not api_key:
        raise RuntimeError("ROBLOX_API_KEY is not configured in the server environment.")
    result = OpenCloudClient(api_key).publish_place(
        candidate["universe_id"], candidate["place_id"], Path(candidate["path"])
    )
    _publish_candidates.pop(candidate_id, None)
    return {
        "published_request_confirmed": True,
        "candidate_id": candidate_id,
        "sha256": candidate["sha256"],
        "roblox": result,
    }


def main() -> None:
    transport = os.getenv("APOLO_MCP_TRANSPORT", "stdio")
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        raise SystemExit("APOLO_MCP_TRANSPORT must be 'stdio' or 'streamable-http'.")


if __name__ == "__main__":
    main()
