# Implementation status

Updated as implementation proceeds. A capability is not "complete" until code, tests, CI evidence and operational documentation exist.

| Capability | Status | Notes |
|---|---|---|
| MCP server entry point | Implemented, CI verification pending | Python MCP SDK; stdio and Streamable HTTP |
| Integration selection | Implemented | Studio compatibility / Open Cloud |
| Rojo project scaffold | Implemented | Source files, not a binary place |
| Project read/write/list | Implemented | Workspace path confinement |
| World/map generator | Partial | Creates a manifest and starter server-side Luau for supported BaseParts; not a full terrain/mesh generator |
| UI generator | Partial | Creates UI spec and starter LocalScript for supported GUI classes; no visual preview or advanced layout engine yet |
| Asset catalog/import/export | Implemented | Local user-provided files; no generative provider included |
| Luau static validation | Partial | Uses installed Luau CLI; explicitly reports skipped if absent |
| Open Cloud place metadata | Implemented adapter, live test pending | Stable Get Place endpoint; requires read scope |
| Headless Open Cloud Luau execution | Implemented adapter, live test pending | Create task, validate Roblox task resource paths, inspect task and logs; gated by environment opt-in |\n| Game test executor | Initial implementation | Declarative checks for instance existence, class, child count, property and attribute; runs through Luau Execution and normalizes pass/fail results; live test pending |
| Open Cloud place publishing | Initial current Assets API adapter | Multipart Update Asset, async operation polling; requires asset read/write permission and valid .rbxl/.rbxlx; not tested against live Roblox |
| Open Cloud metadata / DataStores / asset APIs | Pending | Need endpoint-specific tests and permission mapping |
| Thumbnails / icons / models / audio / animations generation | Pending provider adapters | Requires user-selected provider credentials |
| Autonomous multi-agent execution | Planning interface only | AI client orchestrates task graph; no background agent runtime claimed |
| Manual / approved publishing | Initial | Manual Creator Dashboard handoff documented; GitHub workflow now downloads an artifact from this repo, verifies SHA-256, submits and polls the current Assets API. Configure protected environment reviewers before use |

## Current limitation

The headless mode can generate source/specifications. Rojo build is now available as an adapter and reports blocked when Rojo is absent. Open Cloud Luau Execution now provides headless engine-context script tasks and an initial declarative game-test executor. Test tasks still require a published place and configured API scopes. They do not simulate physics or automatically run server/client scripts; DataModel edits are not automatically persisted. The UI/world generators are starter implementations, not a full visual editor or terrain engine. Asset generation still requires provider adapters and credentials.
