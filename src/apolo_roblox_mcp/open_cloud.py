from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path


class OpenCloudError(RuntimeError):
    pass


class OpenCloudClient:
    """Small stdlib-only client for documented Roblox Open Cloud operations."""

    def __init__(self, api_key: str, timeout: int = 45):
        if not api_key:
            raise ValueError("ROBLOX_API_KEY is not configured.")
        self.api_key = api_key
        self.timeout = timeout

    def publish_place(self, universe_id: str, place_id: str, place_file: Path) -> dict:
        if not universe_id.isdigit() or not place_id.isdigit():
            raise ValueError("Universe ID and Place ID must be numeric.")
        if not place_file.is_file():
            raise FileNotFoundError(str(place_file))
        suffix = place_file.suffix.lower()
        content_type = {
            ".rbxlx": "application/xml",
            ".rbxl": "application/octet-stream",
        }.get(suffix)
        if content_type is None:
            raise ValueError("Place publishing accepts .rbxlx or .rbxl files.")
        url = (
            f"https://apis.roblox.com/universes/v1/{universe_id}/places/"
            f"{place_id}/versions?versionType=Published"
        )
        request = urllib.request.Request(
            url,
            data=place_file.read_bytes(),
            headers={"x-api-key": self.api_key, "Content-Type": content_type},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                try:
                    payload = json.loads(raw) if raw else {}
                except json.JSONDecodeError:
                    payload = {"raw_response": raw}
                return {"http_status": response.status, "response": payload}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OpenCloudError(f"Roblox Open Cloud returned HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise OpenCloudError(f"Could not reach Roblox Open Cloud: {exc.reason}") from exc
