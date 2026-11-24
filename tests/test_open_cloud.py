import json
from pathlib import Path

from apolo_roblox_mcp.open_cloud import OpenCloudClient


class FakeResponse:
    status = 200

    def __init__(self, body=None):
        self.body = body or b'{"path":"universes/123/places/456/versions/7/luau-execution-sessions/session-8/tasks/task-9","state":"QUEUED"}'

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


def test_publish_uses_current_assets_api(monkeypatch, tmp_path: Path):
    place = tmp_path / "place.rbxlx"
    place.write_text("<roblox/>")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["method"] = request.method
        captured["headers"] = dict(request.header_items())
        captured["body"] = request.data
        return FakeResponse(b'{"path":"operations/op-123"}')

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = OpenCloudClient("test-key").publish_place("123", "456", place)
    assert captured["url"] == "https://apis.roblox.com/assets/v1/assets/456"
    assert captured["method"] == "PATCH"
    assert b'"assetType":"Place"' in captured["body"]
    assert b'"published":true' in captured["body"]
    assert b"<roblox/>" in captured["body"]
    assert result["response"]["path"] == "operations/op-123"


def test_create_luau_task_uses_headless_open_cloud(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["method"] = request.method
        captured["body"] = request.data
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = OpenCloudClient("test-key").create_luau_task("123", "456", "return 42", 60)
    assert captured["url"].endswith("/universes/123/places/456/luau-execution-session-tasks")
    assert captured["method"] == "POST"
    assert json.loads(captured["body"]) == {"script": "return 42", "timeout": "60s"}
    assert result["response"]["path"] == "universes/123/places/456/versions/7/luau-execution-sessions/session-8/tasks/task-9"

def test_luau_task_get_and_logs_use_roblox_resource_path(monkeypatch):
    calls = []
    path = "universes/123/places/456/versions/7/luau-execution-sessions/session-8/tasks/task-9"

    def fake_urlopen(request, timeout):
        calls.append(request.full_url)
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OpenCloudClient("test-key")
    client.get_luau_task(path)
    client.get_luau_task_logs(path)
    assert calls == [
        "https://apis.roblox.com/cloud/v2/" + path,
        "https://apis.roblox.com/cloud/v2/" + path + "/logs",
    ]


def test_luau_task_path_rejects_arbitrary_paths():
    import pytest

    client = OpenCloudClient("test-key")
    with pytest.raises(ValueError):
        client.get_luau_task("https://example.com/steal")
    with pytest.raises(ValueError):
        client.get_luau_task("universes/1/places/2/../../secrets")
