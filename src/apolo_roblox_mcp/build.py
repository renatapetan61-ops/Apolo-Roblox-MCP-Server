from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def build_place(root: Path, project: str, output_name: str = "place.rbxlx", timeout: int = 120) -> dict:
    base = (root / project).resolve()
    if root.resolve() not in base.parents or not base.is_dir():
        raise ValueError("Project must be an existing directory inside the workspace.")
    project_file = base / "default.project.json"
    if not project_file.is_file():
        raise FileNotFoundError("default.project.json is missing.")
    rojo = shutil.which("rojo")
    if not rojo:
        return {"status": "blocked", "reason": "Rojo CLI is not installed in the MCP server environment.",
                "install_hint": "Install a pinned Rojo CLI release in the server/CI environment."}
    if not output_name.endswith((".rbxlx", ".rbxl")) or "/" in output_name or "\\" in output_name:
        raise ValueError("Output name must be a simple .rbxlx or .rbxl filename.")
    output = (base / "build" / output_name).resolve()
    if base not in output.parents:
        raise ValueError("Build output must remain inside the project.")
    output.parent.mkdir(exist_ok=True)
    try:
        result = subprocess.run([rojo, "build", str(project_file), "-o", str(output)],
                                cwd=base, capture_output=True, text=True,
                                timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "timeout_seconds": timeout}
    if result.returncode:
        return {"status": "failed", "return_code": result.returncode,
                "stdout": result.stdout[-10000:], "stderr": result.stderr[-10000:]}
    return {"status": "passed", "artifact": str(output) if output.is_file() else None,
            "bytes": output.stat().st_size if output.is_file() else 0,
            "stdout": result.stdout[-10000:], "stderr": result.stderr[-10000:]}
