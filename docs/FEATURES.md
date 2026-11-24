# Feature matrix inspired by ForgeGUI

This is an original implementation plan for equivalent user-facing capabilities. It does not copy ForgeGUI source code, private services, prompts, branding or proprietary assets.

| Area | APOLO capability | Output / integration |
|---|---|---|
| Game thumbnails | Prompt-driven thumbnail creation, revisions and library | Image artifact; optional Open Cloud upload if supported |
| Game icons | Square game icon creation and variants | PNG + metadata |
| GUI artwork | Menu, panel, inventory, shop and dialog artwork | PNG / image asset |
| HUD artwork | Health, currency, status and ability visual elements | PNG + layout specification |
| Avatar artwork | Avatar/profile promotional images | Image artifact |
| 3D models | Prompt-driven textured model jobs | GLB or provider-supported format; conversion/import compatibility checks |
| Classic clothing | Shirt/pants template texture workflows | Roblox-compatible template export; validate template dimensions |
| Music | Original instrumental music generation | Audio artifact; rights/provider metadata |
| Sound effects | Original game SFX generation | Audio artifact; duration/format metadata |
| R15 animation | Animation generation/import workflow | Provider artifact and compatibility report; upload/rig constraints apply |
| GUI kits | Multi-component visual design systems | PNG set + JSON layout + Luau implementation plan |
| GUI controls | Layout, spacing, color, text, border and padding parameters | JSON design tokens / UI source |
| Image editing | Revision prompts for composition, lighting, color and framing | New versioned artifact |
| Asset library | Search, preview, version, tag and approve assets | SQLite metadata + files/artifact storage |
| Export | Individual downloads and ZIP bundles | Deterministic export archive |
| Asset publishing | Upload eligible assets to Roblox | Open Cloud response and asset ID |
| Luau scripting | Generate, explain, refactor and repair scripts | Source files and diffs |
| Game mechanics | Coins, pickups, checkpoints, shops, doors, quests, combat and inventory | Server/client Luau modules |
| Project inspection | Project tree, Rojo mapping, script dependencies | Structured project report |
| Testing | Static validation and headless tests where available | Evidence-based test report |
| Publishing | Manual handoff or approved automatic publish | Release record |

## Quality rules

- Distinguish an image from a functional UI implementation.
- Distinguish a generated 3D file from a Roblox-ready asset.
- Distinguish an animation file from a published Roblox animation asset.
- Do not claim a sound/music asset is licensed for Roblox use without provider rights evidence.
- Show estimated credits/costs before paid generation when the provider exposes pricing.
- Require user review for generated assets and all public releases.
