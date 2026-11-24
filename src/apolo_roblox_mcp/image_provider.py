from __future__ import annotations

import base64
import hashlib
import json
import os
import urllib.error
import urllib.request
import uuid
from pathlib import Path


class ImageGenerationError(RuntimeError):
    pass


_ALLOWED_MODELS = {
    "gpt-image-2.6-sunburst",
    "gpt-image-2.6-flare",
    "gpt-image-2.5-sunburst",
    "gpt-image-2.5-flare",
}
_ALLOWED_SIZES = {"1024x1024", "1536x1024", "1024x1536", "auto"}
_ALLOWED_QUALITIES = {"low", "medium", "high", "xhigh", "max"}


def generate_image_asset(api_key: str, prompt: str, destination: Path,
                         model: str = "gpt-image-2.6-sunburst",
                         size: str = "1024x1024",
                         quality: str = "medium") -> dict:
    if not api_key:
        raise ImageGenerationError("OPENAI_API_KEY is not configured.")
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 4000:
        raise ValueError("prompt must contain 1-4000 characters.")
    if model not in _ALLOWED_MODELS:
        raise ValueError("Unsupported image model.")
    if size not in _ALLOWED_SIZES:
        raise ValueError("Unsupported image size.")
    if quality not in _ALLOWED_QUALITIES:
        raise ValueError("Unsupported image quality.")

    payload = {
        "model": model,
        "prompt": prompt.strip(),
        "size": size,
        "quality": quality,
        "n": 1,
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/images/generations",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ImageGenerationError(f"Image provider returned HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise ImageGenerationError(f"Image generation request failed: {exc}") from exc

    data = result.get("data") or []
    encoded = data[0].get("b64_json") if data and isinstance(data[0], dict) else None
    if not encoded:
        raise ImageGenerationError("Image provider response did not contain b64_json.")
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise ImageGenerationError("Image provider returned invalid base64 image data.") from exc
    if not image_bytes or len(image_bytes) > 20 * 1024 * 1024:
        raise ImageGenerationError("Generated image is empty or exceeds the 20 MiB asset upload limit.")

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_bytes(image_bytes)
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()

    return {
        "path": str(destination),
        "bytes": len(image_bytes),
        "sha256": hashlib.sha256(image_bytes).hexdigest(),
        "model": model,
        "usage": result.get("usage"),
        "review_required": True,
        "next_step": "Review the generated image, then upload it separately through apolo_upload_asset if approved.",
    }
