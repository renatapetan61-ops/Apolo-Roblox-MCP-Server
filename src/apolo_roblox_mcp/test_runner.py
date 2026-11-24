from __future__ import annotations

import json
import re
from typing import Any


class GameTestSpecError(ValueError):
    pass


_ALLOWED_KINDS = {"instance_exists", "is_a", "child_count", "property_equals", "attribute_equals"}
_PATH_PART = re.compile(r"^[A-Za-z_][A-Za-z0-9_ ]*$")


def _lua(value: Any) -> str:
    if isinstance(value, (str, int, float, bool)) and not isinstance(value, complex):
        return json.dumps(value, ensure_ascii=True, allow_nan=False)
    raise GameTestSpecError("Expected values must be strings, finite numbers or booleans.")


def _path(value: Any) -> list[str]:
    if not isinstance(value, str) or not value or len(value) > 512:
        raise GameTestSpecError("Each test requires a non-empty instance path (max 512 chars).")
    parts = value.split(".")
    if len(parts) > 32 or any(not _PATH_PART.fullmatch(part) for part in parts):
        raise GameTestSpecError(f"Invalid instance path: {value!r}")
    if parts[0] not in {"Workspace", "ReplicatedStorage", "ServerStorage",
                        "ServerScriptService", "StarterGui", "StarterPack",
                        "Lighting", "SoundService"}:
        raise GameTestSpecError("Instance paths must start with an allowed DataModel service.")
    return parts


def build_game_test_script(tests: list[dict[str, Any]]) -> str:
    """Build a safe Luau test harness from declarative checks; never eval caller code."""
    if not isinstance(tests, list) or not 1 <= len(tests) <= 100:
        raise GameTestSpecError("Provide between 1 and 100 game tests.")

    lines = [
        "local results = {}",
        "local passed = 0",
        "local failed = 0",
        "local function resolve(path)",
        "    local current = game",
        "    for _, name in ipairs(path) do",
        "        current = current:FindFirstChild(name)",
        "        if not current then return nil end",
        "    end",
        "    return current",
        "end",
        "local function record(id, ok, detail)",
        "    if ok then passed += 1 else failed += 1 end",
        "    table.insert(results, { id = id, passed = ok, detail = detail })",
        "end",
    ]

    for index, spec in enumerate(tests):
        if not isinstance(spec, dict):
            raise GameTestSpecError(f"Test #{index + 1} must be an object.")
        test_id = spec.get("id", f"test_{index + 1}")
        if not isinstance(test_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", test_id):
            raise GameTestSpecError(f"Test #{index + 1} has an invalid id.")
        kind = spec.get("kind")
        if kind not in _ALLOWED_KINDS:
            raise GameTestSpecError(f"Unsupported test kind: {kind!r}")
        parts = _path(spec.get("path"))
        path_lua = "{" + ", ".join(_lua(part) for part in parts) + "}"
        id_lua = _lua(test_id)
        variable = f"instance_{index + 1}"
        lines.append(f"local {variable} = resolve({path_lua})")

        if kind == "instance_exists":
            lines.append(
                f"record({id_lua}, {variable} ~= nil, "
                f"{_lua('Expected instance to exist: ' + spec['path'])})"
            )
        elif kind == "is_a":
            class_name = spec.get("class_name")
            if not isinstance(class_name, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", class_name):
                raise GameTestSpecError("is_a tests require a valid class_name.")
            lines.append(
                f"record({id_lua}, {variable} ~= nil and {variable}:IsA({_lua(class_name)}), "
                f"{_lua('Expected ' + spec['path'] + ' to be a ' + class_name)})"
            )
        elif kind == "child_count":
            expected = spec.get("expected")
            if not isinstance(expected, int) or isinstance(expected, bool) or not 0 <= expected <= 100000:
                raise GameTestSpecError("child_count expected must be an integer from 0 to 100000.")
            lines.append(
                f"record({id_lua}, {variable} ~= nil and #({variable}:GetChildren()) == {expected}, "
                f"{_lua('Expected child count ' + str(expected) + ' at ' + spec['path'])})"
            )
        elif kind == "property_equals":
            prop = spec.get("property")
            if not isinstance(prop, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", prop):
                raise GameTestSpecError("property_equals tests require a valid property.")
            expected_lua = _lua(spec.get("expected"))
            lines.extend([
                f"local ok_{index + 1}, value_{index + 1} = pcall(function()",
                f"    return {variable} and {variable}[{_lua(prop)}]",
                "end)",
                (f"record({id_lua}, ok_{index + 1} and {variable} ~= nil "
                 f"and value_{index + 1} == {expected_lua}, "
                 f"{_lua('Expected property ' + prop + ' at ' + spec['path'])})"),
            ])
        elif kind == "attribute_equals":
            attr = spec.get("attribute")
            if not isinstance(attr, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_ ]{0,63}", attr):
                raise GameTestSpecError("attribute_equals tests require a valid attribute name.")
            expected_lua = _lua(spec.get("expected"))
            lines.append(
                f"record({id_lua}, {variable} ~= nil and "
                f"{variable}:GetAttribute({_lua(attr)}) == {expected_lua}, "
                f"{_lua('Expected attribute ' + attr + ' at ' + spec['path'])})"
            )

    lines.extend([
        ("return { total = #results, passed = passed, failed = failed, "
         "success = failed == 0, results = results }"),
    ])
    script = "\n".join(lines)
    if len(script.encode("utf-8")) > 4 * 1024 * 1024:
        raise GameTestSpecError("Generated game test script exceeds Roblox's 4 MiB limit.")
    return script


def summarize_task(task_response: dict) -> dict:
    """Normalize an Open Cloud task response without assuming it has completed."""
    payload = task_response.get("response", {})
    state = payload.get("state", "STATE_UNSPECIFIED")
    output = payload.get("output", {})
    returned = output.get("results", []) if isinstance(output, dict) else []
    summary = returned[0] if returned and isinstance(returned[0], dict) else None
    error = payload.get("error")
    if state == "COMPLETE" and summary is not None:
        outcome = "passed" if summary.get("success") is True else "failed"
    elif state == "FAILED":
        outcome = "failed"
    elif state == "CANCELLED":
        outcome = "cancelled"
    elif state == "COMPLETE":
        outcome = "failed"
        error = error or {"message": "Roblox task completed without a structured test summary."}
    else:
        outcome = "running"
    return {
        "state": state,
        "outcome": outcome,
        "summary": summary,
        "error": error,
        "raw_output": output,
    }
