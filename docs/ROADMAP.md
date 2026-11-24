# Implementation roadmap

Legend: [x] implemented in code, [~] partial / adapter or integration pending, [ ] not implemented.

## Phase 0 — Repository foundation
- [x] Define product scope and safety boundaries
- [x] Define dual integration architecture
- [x] Define ForgeGUI-inspired capability matrix
- [x] Add runnable Python MCP package and stdio / Streamable HTTP entry point
- [x] Add GitHub Actions CI definition
- [~] Verify latest CI run and supported MCP clients (connected GitHub status endpoint currently exposes no check runs)

## Phase 1 — MCP core
- [x] MCP server entry point and configuration
- [x] Integration selection and capability discovery
- [x] Project workspace tools with path confinement
- [x] Structured validation errors and release candidate hash
- [~] Claude Code / OpenCode / Codex setup documentation; client-specific live connection tests pending

## Phase 2 — Studio-compatible headless workflow
- [x] Rojo project scaffolding
- [x] Luau source editing and project inspection
- [~] Headless Luau validation (requires Luau CLI installed)
- [~] Declarative world/map manifest and starter server Luau generation
- [~] UI design spec and starter ScreenGui LocalScript generation
- [~] Rojo place build adapter (requires Rojo CLI installed)
- [ ] Full terrain, mesh, lighting, physics and live Play testing
- [ ] Optional external Studio MCP connector

## Phase 3 — Open Cloud
- [x] Place metadata read adapter
- [x] Current Assets API place update adapter (multipart, asynchronous operation)
- [x] Poll publication operation and verify isPublished
- [~] Credential and scope diagnostics (real API key and permissions required)
- [ ] General asset create/update and thumbnail management
- [ ] DataStore / MemoryStore operations
- [x] Headless Luau Execution API task submission, status and logs (gated; live test pending)\n- [ ] Remote test runner with TestEZ and reproducible test fixtures

## Phase 4 — ForgeGUI-inspired creation suite
- [~] Local asset library, import, catalog and ZIP export
- [ ] Image / thumbnail / icon / GUI / HUD generation providers
- [ ] Reference-guided visual style profiles and revision workflows
- [ ] Textured 3D model generation and conversion
- [ ] Clothing texture generation and validation
- [ ] Music and sound effect generation
- [ ] R15 animation generation/import
- [ ] Roblox asset upload and moderation/status tracking
- [ ] Provider costs, licensing provenance and usage quotas

## Phase 5 — Full game-building agents
- [x] Deterministic game design task graph
- [ ] Agent orchestration runtime and persistent task state
- [ ] World/map generator expansion
- [ ] Character/NPC systems
- [ ] Inventory, economy, quest, combat and progression systems
- [ ] Multiplayer/server authority review
- [ ] Cross-system integration tests

## Phase 6 — Release and operations
- [x] Manual Creator Dashboard release handoff documented
- [x] Protected GitHub Environment publishing workflow with artifact hash check
- [x] Roblox async publish operation polling in workflow
- [~] Configure `roblox-production` environment required reviewers in repository settings
- [ ] Release manifests, durable approval records and rollback guidance
- [~] Security audit, end-to-end test and first public release

## Acceptance criteria

A phase is complete only when code exists, tests run in GitHub Actions, documented tools match implementation, and the workflow has evidence. Planned tools must not be advertised as implemented.


## Próximo ciclo: criação e validação de jogos completos

1. **Luau Execution e QA:** concluir polling, persistência de IDs de tarefas, relatórios e executor declarativo de testes.
2. **Materializador 3D:** converter descrições de cenas em hierarquias Roblox com Parts, modelos serializados, Terrain e iluminação; distinguir recursos realmente criados dos não suportados.
3. **Assets com IA:** definir interfaces de provedores independentes para imagens, modelos, áudio e animações; importar somente resultados reais e manter licença/origem.
4. **Multiagente:** criar orquestrador persistente com agentes especializados, dependências, tentativas, logs, checkpoint e aprovação humana.
5. **Open Cloud:** concluir uploads de assets, DataStores via Luau Execution, metadados e publicação versionada.
6. **Entrega:** workflow de build, testes em universo de homologação, artefatos com hash e ambiente GitHub protegido para lançamento.

Nenhuma etapa será marcada como concluída sem testes automatizados e evidência de execução. A execução real no Roblox permanece pendente de credenciais, scopes e um universo de teste configurados pelo proprietário.
