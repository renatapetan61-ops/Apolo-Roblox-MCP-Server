# Multi-agent orchestration runtime

APOLO now stores a specialist-agent task graph in SQLite so connected MCP clients can work on one game project without losing task state when the MCP server restarts.

## Specialist roles and dependency graph

1. `architect` — defines the game loop, systems, scene plan and technical boundaries.
2. `luau_engineer` — implements server/client Luau after architecture is complete.
3. `world_builder` — prepares a materializable world specification after architecture is complete.
4. `visual_artist` — prepares image, thumbnail, UI, texture and model deliverables or provider-ready briefs.
5. `audio_designer` — prepares music, sound and animation deliverables or provider-ready briefs.
6. `integrator` — combines the four specialist outputs.
7. `qa_engineer` — prepares and runs game tests against the integrated result.
8. `release_manager` — prepares build evidence, hashes and the approval handoff after QA.

The architect runs first. The four specialist branches can then run in parallel. Integration waits for all four, QA waits for integration, and release preparation waits for QA.

## MCP workflow

- `apolo_create_agent_run` creates a persistent run and its eight tasks.
- `apolo_claim_agent_task` lets a connected worker claim a ready task. Optional `roles` restricts the worker to one or more specialist roles.
- The claim response includes the game brief, constraints and outputs from completed dependencies.
- `apolo_complete_agent_task` stores the worker's result and unlocks downstream work. A failed result can be retried up to three attempts.
- `apolo_get_agent_run` returns current state, task owners, dependencies and deliverables.

Each worker must use a unique `agent_id`. Task leases default to 15 minutes. Expired leases are returned to the queue while attempts remain.

## Persistence and boundaries

The SQLite database is stored at `.apolo/agents.sqlite3` under the configured APOLO workspace. It survives process restarts and uses SQLite WAL mode. Individual task outputs are limited to 1 MiB of JSON.

This is a real persistent orchestration and handoff runtime, but it does **not** spawn language models by itself. Claude Code, OpenCode, Codex or other connected MCP clients act as the worker agents and claim the roles they are configured to perform. Automatic model provisioning, provider billing controls and fully unattended worker spawning remain future work.

Agents should report completion only when the promised files, tests or provider outputs actually exist. A plan or prompt is not equivalent to a generated asset or a tested game.
