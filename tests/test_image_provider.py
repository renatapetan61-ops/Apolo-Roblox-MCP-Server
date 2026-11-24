import base64
import json
from pathlib import Path

import pytest

from apolo_roblox_mcp.image_provider import (
    ImageGenerationError,
    generate_image_asset,
)


class FakeResponse:
    status = 200

    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


def test_generates_and_saves_image_from_provider_response(monkeypatch, tmp_path: Path):
    image_bytes = b"generated-png"
    payload = {"data": [{"b64_json": base64.b64encode(image_bytes).decode()}],
               "usage": {"output_tokens": 900}}
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["payload"] = json.loads(request.data)
        return FakeResponse(json.dumps(payload).encode())

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    target = tmp_path / "assets" / "icon.png"
    result = generate_image_asset("test-key", "A game icon", target)
    assert target.read_bytes() == image_bytes
    assert result["bytes"] == len(image_bytes)
    assert result["review_required"] is True
    assert captured["url"] == "https://api.openai.com/v1/images/generations"
    assert captured["payload"]["model"] == "gpt-image-2.6-sunburst"
    assert captured["headers"]["Authorization"] == "Bearer test-key"


def test_image_generation_validates_prompt_and_model(tmp_path: Path):
    with pytest.raises(ValueError):
        generate_image_asset("key", "", tmp_path / "empty.png")
    with pytest.raises(ValueError):
        generate_image_asset("key", "prompt", tmp_path / "image.png", model="unknown-model")


def test_image_generation_rejects_missing_image_data(monkeypatch, tmp_path: Path):
    def fake_urlopen(request, timeout):
        return FakeResponse(b'{"data": []}')

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    with pytest.raises(ImageGenerationError):
        generate_image_asset("key", "A game icon", tmp_path / "image.png")
