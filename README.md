# APOLO ROBLOX MCP SERVER

A mobile-first, GitHub-native Roblox game development platform controlled by AI agents through MCP. It is designed to create, validate, package and publish Roblox experiences without requiring Roblox Studio to be installed on the developer's phone.

## Core design

APOLO exposes two selectable Roblox integration modes behind one stable MCP tool interface:

1. **Studio MCP Compatibility** — a headless, Studio-independent implementation of Studio-like project operations. It works on source files and place packages using Rojo-compatible project structure, Luau tooling and deterministic build adapters. If an official Roblox Studio MCP endpoint is available elsewhere, an optional connector can forward supported operations to it; it is never a hard dependency.
2. **Roblox Open Cloud** — official cloud APIs for supported operations such as experience/place metadata, asset operations and place publishing, subject to API availability, account permissions, scopes and moderation.

The AI client (Claude Code, OpenCode, Codex or another MCP client) selects a mode using `apolo_select_integration`, or asks its agent to select the best mode. The chosen mode is explicit and visible; no silent fallback may perform a different kind of write.

## Product scope

- Luau project generation, editing, inspection and validation
- Rojo-compatible project structure and place packaging
- Procedural world, map, model and game-system generation
- Game UI/HUD kits, icons, thumbnails and asset library workflows
- Asset-provider adapters for images, 3D models, audio and animation
- Roblox Open Cloud integration and publish approval gates
- Automated CI checks, package artifacts and release records
- MCP tools usable from Claude Code, OpenCode and Codex

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/FEATURES.md](docs/FEATURES.md), [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md), [docs/CLIENT_SETUP.md](docs/CLIENT_SETUP.md), [docs/SECURITY.md](docs/SECURITY.md), and [docs/ROADMAP.md](docs/ROADMAP.md).

## Important limits

- The official Roblox Studio MCP controls a running Studio session. APOLO does not claim to reproduce the Roblox Studio application or its full runtime. Its Studio-compatibility mode provides headless equivalents for supported source/project workflows.
- Open Cloud cannot perform every editor operation or guarantee that every Studio-only feature can be authored or tested remotely.
- A successful build or upload is not proof of gameplay correctness. Runtime validation must be reported separately.
- Asset generation requires configured provider credentials and may incur costs. No generated asset, upload, or publication is claimed unless the provider/API confirms it.
- Publishing is either (a) manual via Creator Dashboard, or (b) automatic only after explicit user approval for that exact release.

## Development

Python 3.11+ is the initial runtime target. Install the package in editable mode once the implementation is available:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

Run tests with `pytest` and the MCP server with `apolo-roblox-mcp`.

## Security

Never commit Roblox API keys, provider keys, cookies, session tokens or generated secrets. Use GitHub Actions secrets or environment variables. Prefer least-privilege Open Cloud API keys. Destructive actions and publishing require explicit approval.
