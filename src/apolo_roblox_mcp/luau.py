from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def validate_luau(root: Path, project: str, relative_path: str, timeout: int = 12) -> dict:
    base = (root / project).resolve()
    if root.resolve() not in base.parents or not base.is_dir():
        raise ValueError("Project must be an existing directory inside the workspace.")
    target = (base / relative_path).resolve()
    if base not in target.parents or target.suffix != ".lua" or not target.is_file():
        raise ValueError("Target must be an existing .lua file inside the project.")
    analyzer = shutil.which("luau-analyze")
    compiler = shutil.which("luau-compile")
    if analyzer:
        command = [analyzer, str(target)]
        tool = "luau-analyze"
    elif compiler:
        command = [compiler, str(target)]
        tool = "luau-compile"
    else:
        return {"status": "skipped", "reason": "Neither luau-analyze nor luau-compile is installed.",
                "install_hint": "Install the official Luau CLI tools in the execution environment."}
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "tool": tool, "timeout_seconds": timeout}
    return {"status": "passed" if result.returncode == 0 else "failed", "tool": tool,
            "return_code": result.returncode, "stdout": result.stdout[-12000:],
            "stderr": result.stderr[-12000:]}
