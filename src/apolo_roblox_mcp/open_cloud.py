from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.request
from pathlib import Path


class OpenCloudError(RuntimeError):
    pass


class OpenCloudClient:
    """Roblox Open Cloud client using an API key with least-privilege permissions."""

    def __init__(self, api_key: str, timeout: int = 45):
        if not api_key:
            raise ValueError("ROBLOX_API_KEY is not configured.")
        self.api_key = api_key
        self.timeout = timeout

    def _request(self, method: str, url: str, data: bytes | None = None,
                 headers: dict[str, str] | None = None) -> dict:
        request_headers = {"x-api-key": self.api_key, **(headers or {})}
        request = urllib.request.Request(url, data=data, headers=request_headers, method=method)
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

    def get_place(self, universe_id: str, place_id: str) -> dict:
        self._validate_ids(universe_id, place_id)
        url = f"https://apis.roblox.com/cloud/v2/universes/{universe_id}/places/{place_id}"
        return self._request("GET", url)

    @staticmethod
    def _validate_ids(universe_id: str, place_id: str) -> None:
        if not universe_id.isdigit() or not place_id.isdigit():
            raise ValueError("Universe ID and Place ID must be numeric.")

    def publish_place(self, universe_id: str, place_id: str, place_file: Path) -> dict:
        self._validate_ids(universe_id, place_id)
        if not place_file.is_file():
            raise FileNotFoundError(str(place_file))
        content_type = {
            ".rbxlx": "application/xml",
            ".rbxl": "application/octet-stream",
        }.get(place_file.suffix.lower())
        if content_type is None:
            raise ValueError("Place publishing accepts .rbxlx or .rbxl files.")

        # Current Roblox guidance uses the Assets API Update Asset endpoint.
        # It is multipart and asynchronous: a returned operation must be polled.
        boundary = "----APOLO" + secrets.token_hex(16)
        metadata = json.dumps({
            "assetId": int(place_id), "assetType": "Place", "published": True
        }, separators=(",", ":"))
        file_bytes = place_file.read_bytes()
        filename = place_file.name.replace('"', "").replace("\r", "").replace("\n", "")
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="request"\r\n'
            "Content-Type: application/json\r\n\r\n"
            f"{metadata}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="fileContent"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode() + file_bytes + f"\r\n--{boundary}--\r\n".encode()
        url = f"https://apis.roblox.com/assets/v1/assets/{place_id}"
        return self._request(
            "PATCH", url, body,
            {"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )


    def create_luau_task(self, universe_id: str, place_id: str, script: str,
                         timeout_seconds: int = 300) -> dict:
        self._validate_ids(universe_id, place_id)
        if not script.strip() or len(script.encode("utf-8")) > 4 * 1024 * 1024:
            raise ValueError("Luau script must be non-empty and no larger than 4 MiB.")
        if not 1 <= timeout_seconds <= 300:
            raise ValueError("Luau task timeout must be between 1 and 300 seconds.")
        url = (f"https://apis.roblox.com/cloud/v2/universes/{universe_id}/places/"
               f"{place_id}/luau-execution-session-tasks")
        body = json.dumps({"script": script, "timeout": f"{timeout_seconds}s"}).encode()
        return self._request("POST", url, body, {"Content-Type": "application/json"})

    @staticmethod
    def _validate_luau_task_path(task_path: str) -> None:
        # Roblox documents four resource path forms. Accept only those exact shapes;
        # never accept a URL, query, fragment, traversal or arbitrary API path.
        import re

        patterns = (
            r"^universes/\d+/places/\d+/luau-execution-session-tasks/[A-Za-z0-9_-]+$",
            r"^universes/\d+/places/\d+/versions/\d+/luau-execution-session-tasks/[A-Za-z0-9_-]+$",
            r"^universes/\d+/places/\d+/luau-execution-sessions/[A-Za-z0-9_-]+/tasks/[A-Za-z0-9_-]+$",
            r"^universes/\d+/places/\d+/versions/\d+/luau-execution-sessions/[A-Za-z0-9_-]+/tasks/[A-Za-z0-9_-]+$",
        )
        if not isinstance(task_path, str) or not any(re.fullmatch(p, task_path) for p in patterns):
            raise ValueError("Invalid Roblox Luau task resource path.")

    def get_luau_task(self, task_path: str) -> dict:
        self._validate_luau_task_path(task_path)
        return self._request("GET", "https://apis.roblox.com/cloud/v2/" + task_path)

    def get_luau_task_logs(self, task_path: str) -> dict:
        self._validate_luau_task_path(task_path)
        return self._request("GET", "https://apis.roblox.com/cloud/v2/" + task_path + "/logs")


    def create_asset(self, asset_type: str, asset_file: Path, display_name: str,
                     description: str, creator_type: str, creator_id: str) -> dict:
        """Create one Roblox asset through the Open Cloud Assets API."""
        if creator_type not in {"user", "group"} or not creator_id.isdigit():
            raise ValueError("creator_type must be 'user' or 'group' and creator_id must be numeric.")
        if not display_name.strip() or len(display_name) > 100:
            raise ValueError("Asset display_name must contain 1-100 characters.")
        if len(description) > 1000:
            raise ValueError("Asset description must not exceed 1000 characters.")
        if not asset_file.is_file():
            raise FileNotFoundError(str(asset_file))
        if asset_file.stat().st_size > 20 * 1024 * 1024:
            raise ValueError("Roblox Assets API content uploads are limited to 20 MiB per asset.")

        supported = {
            "Image": {".png", ".jpg", ".jpeg", ".bmp", ".tga"},
            "Decal": {".png", ".jpg", ".jpeg", ".bmp", ".tga"},
            "Model": {".fbx", ".gltf", ".glb", ".rbxm", ".rbxmx"},
            "Audio": {".mp3", ".ogg", ".wav", ".flac"},
            "Animation": {".rbxm", ".rbxmx"},
            "Video": {".mp4", ".mov"},
        }
        suffix = asset_file.suffix.lower()
        if asset_type not in supported or suffix not in supported[asset_type]:
            raise ValueError(f"Unsupported file extension {suffix!r} for Roblox asset type {asset_type!r}.")
        content_types = {
            ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".bmp": "image/bmp", ".tga": "image/tga",
            ".fbx": "model/fbx", ".gltf": "model/gltf+json",
            ".glb": "model/gltf-binary", ".rbxm": "model/x-rbxm",
            ".rbxmx": "model/x-rbxm", ".mp3": "audio/mpeg",
            ".ogg": "audio/ogg", ".wav": "audio/wav", ".flac": "audio/flac",
            ".mp4": "video/mp4", ".mov": "video/mov",
        }
        creator_field = "userId" if creator_type == "user" else "groupId"
        metadata = {
            "assetType": asset_type,
            "displayName": display_name.strip(),
            "description": description,
            "creationContext": {"creator": {creator_field: creator_id}},
        }
        boundary = "----APOLO" + secrets.token_hex(16)
        filename = asset_file.name.replace('"', "").replace("\r", "").replace("\n", "")
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="request"\r\n'
            "Content-Type: application/json\r\n\r\n"
            f"{json.dumps(metadata, separators=(',', ':'))}\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="fileContent"; filename="{filename}"\r\n'
            f"Content-Type: {content_types[suffix]}\r\n\r\n"
        ).encode() + asset_file.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
        return self._request(
            "POST", "https://apis.roblox.com/assets/v1/assets", body,
            {"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )

    def get_operation(self, operation_id: str) -> dict:
        if not operation_id or "/" in operation_id or ".." in operation_id:
            raise ValueError("Invalid Roblox operation ID.")
        url = f"https://apis.roblox.com/assets/v1/operations/{operation_id}"
        return self._request("GET", url)
