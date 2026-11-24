from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    workspace: Path
    default_integration: str
    roblox_api_key: str | None
    universe_id: str | None
    place_id: str | None

    @classmethod
    def from_env(cls) -> Settings:
        mode = os.getenv("APOLO_DEFAULT_INTEGRATION", "studio_compat")
        if mode not in {"studio_compat", "open_cloud"}:
            mode = "studio_compat"
        workspace = Path(os.getenv("APOLO_WORKSPACE", "./workspace")).expanduser().resolve()
        workspace.mkdir(parents=True, exist_ok=True)
        return cls(
            workspace=workspace,
            default_integration=mode,
            roblox_api_key=os.getenv("ROBLOX_API_KEY") or None,
            universe_id=os.getenv("ROBLOX_UNIVERSE_ID") or None,
            place_id=os.getenv("ROBLOX_PLACE_ID") or None,
        )
