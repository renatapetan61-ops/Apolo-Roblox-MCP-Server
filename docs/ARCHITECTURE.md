# Architecture

## High-level flow

AI agent (Claude Code / OpenCode / Codex)
→ APOLO MCP Server
→ integration router
→ selected adapter
→ project workspace / Roblox Open Cloud

The MCP server is the single stable interface. Adapters implement capabilities and declare which operations they support. Tools must return structured results including `mode`, `status`, `operation_id` when applicable, warnings and evidence.

## Two integration modes

### A. Studio MCP Compatibility (headless)

Purpose: provide Studio-like development capabilities without requiring Roblox Studio or its official MCP server.

- Treat the Git repository as the authoritative project.
- Use a Rojo-compatible project tree and `default.project.json`.
- Generate/edit Luau, project metadata, UI definitions and deterministic scene/build descriptions.
- Use available headless Luau tooling (for example luau-analyze / luau-compile) when installed; report unavailable validators as skipped, never passed.
- Package the project through a pinned, reproducible build toolchain.
- Optionally connect to an external official Studio MCP endpoint if the user explicitly configures one. This is an enhancement, not a prerequisite.
- Operations requiring a live Studio DataModel, Play mode, plugin UI or Studio-only editor APIs must return `unsupported_without_studio` or use an explicitly configured remote test runner.

This is **compatibility with Studio-oriented workflows**, not a claim that the official Studio MCP server itself can run without Studio.

### B. Roblox Open Cloud

Purpose: interact with Roblox-hosted resources through official APIs.

- Store API keys only in environment variables / GitHub Secrets.
- Check key permissions before mutations.
- Use documented Open Cloud endpoints and API versions.
- Distinguish asset upload, place publishing, metadata and DataStore operations; do not conflate them.
- Respect Roblox moderation, ownership, experience/place IDs, quotas and API-specific constraints.
- Return the Roblox response identifiers and URLs as evidence.

## Integration selection

`apolo_select_integration(mode)` accepts `studio_compat` or `open_cloud`. The current selection is session-scoped unless the client explicitly persists configuration. Tools that mutate Roblox resources must state which adapter they will use. If a requested operation is unsupported in the selected mode, explain that and ask before switching modes.

An agent may choose automatically only after inspecting the task and explaining the choice. The user can always override it.

## Game project pipeline

1. Intake: game brief, target platform, audience, mechanics, art direction and references.
2. Plan: feature breakdown, dependency graph, asset budget and acceptance criteria.
3. Generate: Rojo project, Luau modules, map/build manifests, UI specifications and asset requests.
4. Validate: static checks, dependency checks, schema checks, security review and available headless tests.
5. Package: deterministic place package / build artifacts with hashes and manifest.
6. Review: show changed files, warnings, test evidence and release diff.
7. Publish: manual Creator Dashboard handoff or automatic Open Cloud publish after per-release approval.
8. Verify: record API response, published version identifiers and post-publish checks.

## Asset pipeline

A provider-neutral interface handles image, GUI, thumbnail, icon, texture, 3D model, audio and animation jobs. Each job has a stable request ID, provider, prompt, parameters, cost estimate when available, state, artifact metadata and moderation status. Generation and Roblox upload are separate operations. A generated PNG is not a functional Roblox ScreenGui; interactive controls require corresponding instances and Luau logic.

## Reliability

- Idempotency keys for generation/upload/publish requests where supported.
- Never automatically retry an operation with unknown outcome if it could charge or publish twice.
- Persist operation records and artifact hashes.
- Pin toolchain versions in CI.
- Fail closed on missing credentials, insufficient scopes or unknown publish target.
