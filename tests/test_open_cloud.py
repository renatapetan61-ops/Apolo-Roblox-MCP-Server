from pathlib import Path

from apolo_roblox_mcp.open_cloud import OpenCloudClient


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return b'{"path":"operations/op-123"}'


def test_publish_uses_current_assets_api(monkeypatch, tmp_path: Path):
    place = tmp_path / "place.rbxlx"
    place.write_text("<roblox/>")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["method"] = request.method
        captured["headers"] = dict(request.header_items())
        captured["body"] = request.data
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    result = OpenCloudClient("test-key").publish_place("123", "456", place)
    assert captured["url"] == "https://apis.roblox.com/assets/v1/assets/456"
    assert captured["method"] == "PATCH"
    assert b'"assetType":"Place"' in captured["body"]
    assert b'"published":true' in captured["body"]
    assert b"<roblox/>" in captured["body"]
    assert result["response"]["path"] == "operations/op-123"
