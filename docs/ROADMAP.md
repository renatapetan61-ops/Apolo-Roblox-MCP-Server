# Implementation roadmap

## Phase 0 — Repository foundation
- [x] Define product scope and safety boundaries
- [x] Define dual integration architecture
- [x] Define ForgeGUI-inspired capability matrix
- [ ] Add runnable MCP server package
- [ ] Add tests and CI

## Phase 1 — MCP core
- [ ] MCP server entry point and configuration
- [ ] Integration selection and capability discovery
- [ ] Project workspace tools
- [ ] Structured errors, operation IDs and audit events
- [ ] Claude Code / OpenCode / Codex setup documentation

## Phase 2 — Studio-compatible headless workflow
- [ ] Rojo project scaffolding
- [ ] Luau source editing and project inspection
- [ ] Headless Luau validation
- [ ] Instance / scene manifest generator
- [ ] UI layout and Luau controller generation
- [ ] Reproducible place packaging
- [ ] Optional external Studio MCP connector

## Phase 3 — Open Cloud
- [ ] Credential and scope diagnostics
- [ ] Experience/place metadata
- [ ] Asset API capability registry
- [ ] DataStore tools
- [ ] Place publishing
- [ ] API response verification and safe retries

## Phase 4 — ForgeGUI-inspired creation suite
- [ ] Image / thumbnail / icon / GUI / HUD providers
- [ ] GUI kits and design tokens
- [ ] Textured 3D model provider
- [ ] Clothing texture workflows
- [ ] Music and sound effect providers
- [ ] R15 animation provider
- [ ] Asset library, revisions and ZIP export
- [ ] Cost/credit visibility and moderation metadata

## Phase 5 — Full game-building agents
- [ ] Game brief and design document
- [ ] World/map generator
- [ ] Character/NPC systems
- [ ] Inventory, economy, quest, combat and progression systems
- [ ] Multiplayer/server authority review
- [ ] Cross-system integration tests

## Phase 6 — Release and operations
- [ ] Manual Creator Dashboard release handoff
- [ ] Approval-bound automatic publishing
- [ ] Protected GitHub environments
- [ ] Release manifests and rollback guidance
- [ ] Security audit, documentation and versioned release

## Acceptance criteria

A phase is complete only when code exists, tests run in GitHub Actions, documented tools match implementation, and the workflow has evidence. Planned tools must not be advertised as implemented.
