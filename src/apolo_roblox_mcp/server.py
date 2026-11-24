from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid
import zipfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from .agents import plan_game
from .assets import export_assets, import_asset, list_assets
from .build import build_place
from .config import Settings
from .luau import validate_luau
from .open_cloud import OpenCloudClient
from .test_runner import build_game_test_script, summarize_task
from .ui import create_ui_spec
from .workspace import create_project, list_files, safe_path, write_text
from .worlds import build_world_manifest

settings = Settings.from_env()
mcp = FastMCP("APOLO Roblox MCP Server")
_selected_mode = settings.default_integration
_publish_candidates: dict[str, dict] = {}
_TASK_REGISTRY = settings.workspace / ".apolo" / "luau_tasks.json"
_TASK_LOCK = threading.Lock()


def _load_luau_tasks() -> dict[str, dict]:
    if not _TASK_REGISTRY.is_file():
        return {}
    try:
        payload = json.loads(_TASK_REGISTRY.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


_luau_tasks: dict[str, dict] = _load_luau_tasks()


def _persist_luau_task(task_id: str, record: dict) -> None:
    with _TASK_LOCK:
        _luau_tasks[task_id] = record
        _TASK_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        temporary = _TASK_REGISTRY.with_suffix(".tmp")
        temporary.write_text(json.dumps(_luau_tasks, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, _TASK_REGISTRY)


CAPABILITIES = {
    "studio_compat": [
        "project.scaffold", "project.inspect", "luau.write", "luau.validate", "project.build",
        "world.manifest", "ui.spec", "project.package",
    ],
    "open_cloud": [
        "cloud.place.publish", "cloud.place.metadata", "cloud.publish.operation_status",
        "cloud.luau.execute", "cloud.luau.task_status", "cloud.game_tests.run",
        "cloud.game_tests.results",
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
            "project.inspect", "luau.write", "project.package", "world.manifest", "ui.spec",
            "asset.library", "luau.validate", "game.plan", "project.build",
            "cloud.place.publish_with_approval", "cloud.place.metadata", "cloud.publish.operation_status", "cloud.luau.execute", "cloud.luau.task_status", "cloud.game_tests.run", "cloud.game_tests.results",
        ],
        "planned": {
            "studio_compat": ["live.playtest", "terrain.generator", "mesh.generator"],
            "open_cloud": ["asset.operations", "datastores"],
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
        "path": str(artifact), "sha256": digest, "created_at": time.time(), "state": "prepared",
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
    """Submit a prepared place for publishing after exact release-specific user approval."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before publishing.")
    if os.getenv("APOLO_ALLOW_DIRECT_PUBLISH", "false").lower() != "true":
        raise PermissionError("Direct MCP publishing is disabled by default. Use the protected GitHub Actions roblox-production environment for a human-reviewed release.")
    candidate = _publish_candidates.get(candidate_id)
    if candidate is None:
        raise ValueError("Unknown or expired release candidate. Prepare it again.")
    if candidate["state"] != "prepared":
        raise RuntimeError("This candidate was already submitted or has an uncertain outcome; do not retry blindly.")
    if time.time() - candidate["created_at"] > 1800:
        _publish_candidates.pop(candidate_id, None)
        raise ValueError("Release candidate expired after 30 minutes. Prepare and approve a new candidate.")
    expected = f"APPROVE ROBLOX RELEASE {candidate_id}"
    if approval_phrase != expected:
        raise PermissionError("Approval phrase does not match this release candidate.")
    artifact = Path(candidate["path"])
    if not artifact.is_file():
        raise FileNotFoundError("Approved artifact no longer exists.")
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if digest != candidate["sha256"]:
        _publish_candidates.pop(candidate_id, None)
        raise ValueError("Artifact changed after approval; prepare and approve a new candidate.")
    api_key = settings.roblox_api_key
    if not api_key:
        raise RuntimeError("ROBLOX_API_KEY is not configured in the server environment.")
    candidate["state"] = "submitting"
    try:
        result = OpenCloudClient(api_key).publish_place(
            candidate["universe_id"], candidate["place_id"], artifact
        )
    except Exception:
        candidate["state"] = "outcome_unknown"
        raise
    operation = result.get("response", {}).get("path", "")
    candidate["state"] = "submitted"
    candidate["operation_id"] = operation.rsplit("/", 1)[-1] if operation else None
    return {
        "upload_accepted": True,
        "publication_completed": False,
        "candidate_id": candidate_id,
        "sha256": candidate["sha256"],
        "roblox": result,
        "next_step": "Poll apolo_get_publish_operation until done=true; verify response.isPublished=true.",
    }

@mcp.tool()
def apolo_generate_world(project: str, name: str, description: str, theme: str,
                         size: str, objects: list[dict]) -> dict:
    """Generate a validated declarative world/map manifest in the selected Studio-compatible project."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat to generate project world manifests.")
    return build_world_manifest(settings.workspace, project, name, description, theme, size, objects)


@mcp.tool()
def apolo_generate_ui_spec(project: str, screen_name: str, purpose: str,
                           palette: dict, components: list[dict]) -> dict:
    """Generate a Roblox UI design specification. This creates a spec, not a live ScreenGui."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat to generate UI specifications.")
    return create_ui_spec(settings.workspace, project, screen_name, purpose, palette, components)


@mcp.tool()
def apolo_validate_luau(project: str, path: str) -> dict:
    """Run luau-analyze or luau-compile if installed; otherwise report validation as skipped."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat to validate local Luau files.")
    return validate_luau(settings.workspace, project, path)


@mcp.tool()
def apolo_import_asset(project: str, source_path: str, category: str, name: str) -> dict:
    """Import a user-provided asset file into the project's local asset library; does not upload to Roblox."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat to manage the local asset library.")
    return import_asset(settings.workspace, project, source_path, category, name)


@mcp.tool()
def apolo_list_assets(project: str) -> dict:
    """List assets imported into the local project library."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat to inspect the local asset library.")
    return {"assets": list_assets(settings.workspace, project)}


@mcp.tool()
def apolo_export_assets(project: str) -> dict:
    """Export the local asset library to a ZIP archive with a SHA-256 digest."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat to export local assets.")
    return export_assets(settings.workspace, project)


@mcp.tool()
def apolo_plan_game(brief: str, genre: str, target: str, constraints: list[str]) -> dict:
    """Create an AI-agent task graph for a game brief; the connected AI client orchestrates execution."""
    return plan_game(brief, genre, target, constraints)



@mcp.tool()
def apolo_get_place_metadata(universe_id: str, place_id: str) -> dict:
    """Read place metadata from Roblox Open Cloud; requires read permission."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before calling Roblox Open Cloud.")
    if not settings.roblox_api_key:
        raise RuntimeError("ROBLOX_API_KEY is not configured.")
    return OpenCloudClient(settings.roblox_api_key).get_place(universe_id, place_id)


@mcp.tool()
def apolo_get_publish_operation(candidate_id: str) -> dict:
    """Poll the asynchronous Roblox publishing operation for a submitted release."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before calling Roblox Open Cloud.")
    candidate = _publish_candidates.get(candidate_id)
    if candidate is None or candidate.get("state") != "submitted":
        raise ValueError("No submitted operation is recorded for this candidate.")
    operation_id = candidate.get("operation_id")
    if not operation_id:
        raise RuntimeError("Roblox did not return an operation ID; verify the response manually.")
    if not settings.roblox_api_key:
        raise RuntimeError("ROBLOX_API_KEY is not configured.")
    result = OpenCloudClient(settings.roblox_api_key).get_operation(operation_id)
    payload = result.get("response", {}).get("response", {})
    done = result.get("response", {}).get("done") is True
    published = done and payload.get("isPublished") is True
    if done:
        candidate["state"] = "completed" if published else "failed"
    return {"candidate_id": candidate_id, "operation_id": operation_id,
            "done": done, "published": published, "roblox": result}



@mcp.tool()
def apolo_build_place(project: str, output_name: str = "place.rbxlx") -> dict:
    """Build a Roblox place headlessly with Rojo if installed; skipped builds are never marked passed."""
    if _selected_mode != "studio_compat":
        raise RuntimeError("Select studio_compat before building a local project.")
    return build_place(settings.workspace, project, output_name)


@mcp.tool()
def apolo_execute_luau(universe_id: str, place_id: str, script: str,
                       confirm_live_execution: bool = False,
                       timeout_seconds: int = 300) -> dict:
    """Run Luau headlessly in a Roblox place via Open Cloud. Requires explicit opt-in and execution scopes."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before executing Roblox Luau.")
    if not confirm_live_execution or os.getenv("APOLO_ALLOW_LUAU_EXECUTION", "false").lower() != "true":
        raise PermissionError("Cloud Luau execution is disabled. Set APOLO_ALLOW_LUAU_EXECUTION=true and explicitly confirm this invocation.")
    if not settings.roblox_api_key:
        raise RuntimeError("ROBLOX_API_KEY is not configured.")
    result = OpenCloudClient(settings.roblox_api_key).create_luau_task(
        universe_id, place_id, script, timeout_seconds
    )
    resource = result.get("response", {}).get("path")
    if not resource:
        return {"accepted": False, "roblox": result}
    task_id = resource.rsplit("/", 1)[-1]
    _persist_luau_task(task_id, {
        "path": resource, "universe_id": universe_id, "place_id": place_id,
        "kind": "luau", "created_at": time.time(),
    })
    return {"accepted": True, "task_id": task_id, "resource_path": resource,
            "roblox": result,
            "warning": "Task runs against a Roblox place version. DataModel edits are not automatically persisted; cloud services called by the script may affect real data."}


@mcp.tool()
def apolo_run_game_tests(universe_id: str, place_id: str, tests: list[dict],
                         confirm_live_execution: bool = False,
                         timeout_seconds: int = 300) -> dict:
    """Run declarative game QA checks against a published Roblox place using headless Luau Execution."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before running Roblox game tests.")
    if not confirm_live_execution or os.getenv("APOLO_ALLOW_LUAU_EXECUTION", "false").lower() != "true":
        raise PermissionError("Cloud game tests are disabled. Set APOLO_ALLOW_LUAU_EXECUTION=true and explicitly confirm this invocation.")
    if not settings.roblox_api_key:
        raise RuntimeError("ROBLOX_API_KEY is not configured.")
    script = build_game_test_script(tests)
    result = OpenCloudClient(settings.roblox_api_key).create_luau_task(
        universe_id, place_id, script, timeout_seconds
    )
    resource = result.get("response", {}).get("path")
    if not resource:
        return {"accepted": False, "reason": "Roblox response did not include a task resource path.", "roblox": result}
    task_id = resource.rsplit("/", 1)[-1]
    _persist_luau_task(task_id, {
        "path": resource, "universe_id": universe_id, "place_id": place_id,
        "kind": "game_test", "test_count": len(tests), "created_at": time.time(),
    })
    return {
        "accepted": True, "task_id": task_id, "test_count": len(tests),
        "resource_path": resource, "roblox": result,
        "next_step": "Call apolo_get_game_test_results with this task_id until outcome is passed or failed.",
        "warning": "Tests execute against the selected published place version. Avoid destructive DataStore writes; use a dedicated test universe.",
    }


@mcp.tool()
def apolo_get_game_test_results(task_id: str) -> dict:
    """Poll a game test task and return normalized pass/fail status, assertions and logs."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before querying Roblox game tests.")
    task = _luau_tasks.get(task_id)
    if task is None or task.get("kind") != "game_test":
        raise ValueError("Unknown game test task ID in this MCP server process.")
    if not settings.roblox_api_key:
        raise RuntimeError("ROBLOX_API_KEY is not configured.")
    client = OpenCloudClient(settings.roblox_api_key)
    raw = client.get_luau_task(task["path"])
    summary = summarize_task(raw)
    logs = client.get_luau_task_logs(task["path"])
    return {
        "task_id": task_id, "test_count": task["test_count"],
        **summary, "logs": logs.get("response", {}),
        "roblox_task": raw.get("response", {}),
    }


@mcp.tool()
def apolo_get_luau_task(task_id: str) -> dict:
    """Get state and return values for a previously submitted headless Luau task."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before querying Roblox Luau tasks.")
    task = _luau_tasks.get(task_id)
    if task is None:
        raise ValueError("Unknown task ID in this MCP server process.")
    if not settings.roblox_api_key:
        raise RuntimeError("ROBLOX_API_KEY is not configured.")
    return OpenCloudClient(settings.roblox_api_key).get_luau_task(task["path"])


@mcp.tool()
def apolo_get_luau_task_logs(task_id: str) -> dict:
    """Retrieve print output and structured logs for a previously submitted Luau task."""
    if _selected_mode != "open_cloud":
        raise RuntimeError("Select open_cloud before querying Roblox Luau logs.")
    task = _luau_tasks.get(task_id)
    if task is None:
        raise ValueError("Unknown task ID in this MCP server process.")
    if not settings.roblox_api_key:
        raise RuntimeError("ROBLOX_API_KEY is not configured.")
    return OpenCloudClient(settings.roblox_api_key).get_luau_task_logs(task["path"])

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
