# ForgeGUI Create parity specification

Source reviewed: https://forgegui.com/create (accessed 2026-11-24), plus the ForgeGUI MCP and ForgeGUI Code product documentation linked from the site. This document records the feature scope APOLO intends to implement independently. It is not an assertion that every capability is already implemented.

## Directly advertised on ForgeGUI /create

| ForgeGUI feature | APOLO equivalent requirement |
|---|---|
| Chat-driven asset generation | MCP tools accept natural-language briefs and return job IDs, status and artifacts |
| Multiple assets at once | Batch jobs with per-item status, stable IDs, retry safety and consolidated ZIP export |
| Thumbnails | Game thumbnail generation |
| Icons | Game/app icon generation |
| 3D assets | Text-to-3D asset generation with GLB export and Roblox compatibility report |
| Prompt-to-result workflow | Prompt intake, clarification, generation, preview, revision and approval |
| PNG export | Export individual PNG files |
| ZIP export | Export selected assets or complete asset sets as ZIP |
| GLB export | Export 3D assets in GLB where provider supports it |
| Reference-guided style | Upload a reference image and derive reusable style tokens (palette, borders, typography, lighting, mood) |
| Complete UI sets in one generation | Generate coherent inventory, HUD, health bars, skill icons and buttons under one shared design brief |
| Cross-platform game UI | Export neutral assets for Roblox, UEFN, Unity, Unreal, Minecraft and mobile projects |
| Fine-grained controls | Edit layout, colors, text overlays, borders and padding with structured design tokens |
| Export and share | Download, package, version and share generated outputs |
| AI trained for game UI patterns | Use a pluggable game-asset provider layer and Roblox-aware prompt templates |
| Community gallery | Optional public gallery with explicit opt-in and moderation |
| Free starter credits / premium credits | Usage meter, quotas, cost estimate and provider billing metadata; no fake credit balances |
| Different generation costs | Per-task cost/credit estimate and actual usage returned by provider |
| Commercial usage license | Store provider/license provenance and show the exact rights supplied by the configured provider |
| Public catalog consent | Explicit consent before publishing eligible free/trial outputs to a public asset gallery |
| Private paid outputs by default | Private-by-default storage unless user explicitly shares/publishes |

## Additional ForgeGUI MCP / Code workflows

These are documented across ForgeGUI's MCP and Code pages and are included in APOLO's broader parity target:

- Roblox thumbnails, GUI images, HUD and avatar images
- Classic clothing textures
- Music and sound effects
- R15 animation workflows
- Textured 3D model generation
- Asset library review and revisions
- Roblox asset publishing when account authorization and Roblox APIs permit it
- Luau scripting assistance and explanations
- Coin pickups, checkpoints, shops and other game mechanics
- Script debugging, test instructions and revision workflows

## APOLO-specific additions

- Studio-compatible headless project authoring with no Studio installation requirement
- Roblox Open Cloud integration as a separate selectable mode
- Rojo-compatible project source and reproducible build packages
- GitHub Actions validation, artifacts and release history
- Explicit user approval bound to an immutable release hash before automatic publication
- Manual Creator Dashboard handoff
- Client setup for Claude Code, OpenCode and Codex

## Important product distinctions

- Reference-guided visual consistency is a reusable style profile, not simply passing an image once to a model.
- A UI artwork image is not a functional Roblox GUI. APOLO must create the corresponding UI hierarchy, layout metadata and Luau behavior separately.
- A GLB is an interchange artifact, not automatically a Roblox-published model.
- Batch generation must not hide individual failures or duplicate billable requests.
- Credits and commercial rights are provider-specific. APOLO must show the configured provider's actual terms rather than copying ForgeGUI's claims.
- The community gallery must be opt-in; projects and assets remain private by default.
