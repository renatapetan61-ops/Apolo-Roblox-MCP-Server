# Implementation status

Updated as implementation proceeds. A capability is not "complete" until code, tests, CI evidence and operational documentation exist.

| Capability | Status | Notes |
|---|---|---|
| MCP server entry point | Implemented, CI passing | Python MCP SDK; stdio and Streamable HTTP; lint and 29 unit tests passed in GitHub Actions at run #145 |
| Integration selection | Implemented | Studio compatibility / Open Cloud |
| Rojo project scaffold | Implemented | Source files, not a binary place |
| Project read/write/list | Implemented | Workspace path confinement |
| World/map generator | Partial | Manifest generator plus initial Open Cloud materializer for Parts, grouped Models, Terrain blocks and Lighting; arbitrary meshes/imported models remain pending |
| UI generator | Partial | Creates UI spec and starter LocalScript for supported GUI classes; no visual preview or advanced layout engine yet |
| Asset catalog/import/export | Implemented | Local asset library/import/export; generated PNGs are saved into the same project workspace |
| Luau static validation | Partial | Uses installed Luau CLI; explicitly reports skipped if absent |
| Open Cloud place metadata | Implemented adapter, live test pending | Stable Get Place endpoint; requires read scope |
| Headless Open Cloud Luau execution | Implemented adapter, live test pending | Create task, validate Roblox task resource paths, inspect task and logs; gated by environment opt-in |
| Game test executor | Initial implementation, CI unit tests passing | Declarative checks for instance existence, class, child count, property and attribute; live Roblox test pending |
| Rojo place artifact build | First build succeeded | Pinned Rojo 7.7.1; starter project built to .rbxlx, SHA-256 recorded and artifact uploaded; build never publishes |
| Open Cloud place publishing | Initial current Assets API adapter | Multipart Update Asset, async operation polling; requires asset read/write permission and valid .rbxl/.rbxlx; not tested against live Roblox |
| Open Cloud asset upload | Initial adapter, live test pending | Multipart upload for Images, Decals, Models, Audio and Animation; 20 MiB limit, explicit confirmation and async operation polling |
| Open Cloud DataStores | Initial read/update adapters, live test pending | List stores, list entries, read entries and update existing entries; write requires explicit opt-in; create/delete remain pending |
| AI image assets | Initial OpenAI Images provider | PNG generation for icons, thumbnails, UI art and textures; explicit billing/confirmation gate |
| 3D meshes / clothing / audio / animation generation | Pending provider adapters | Requires modality-specific providers and file validation |
| Multi-agent orchestration | Initial persistent runtime | SQLite task DAG, specialist roles, dependency handoffs, worker leases and retry handling; connected MCP clients are the workers, no model spawning yet |
| Manual / approved publishing | Initial | Manual Creator Dashboard handoff documented; GitHub workflow now downloads an artifact from this repo, verifies SHA-256, submits and polls the current Assets API. Configure protected environment reviewers before use |

## Current limitation

The headless mode can generate source/specifications and has an initial Open Cloud world materializer for Parts, grouped Models, Terrain blocks and Lighting. The game-test executor has CI unit coverage, but no live Roblox test has been run. DataModel edits are ephemeral by default; optional SavePlaceAsync uses SaveWithoutPublish=true and is separately gated because it overwrites saved place state and only works when Roblox has enabled the API for that place. Luau Execution does not simulate physics or automatically start server/client scripts. Arbitrary meshes, advanced terrain shaping, 3D/clothing/audio/animation providers and automatic model spawning remain incomplete. The current multi-agent runtime coordinates connected MCP workers but does not launch model processes itself.
