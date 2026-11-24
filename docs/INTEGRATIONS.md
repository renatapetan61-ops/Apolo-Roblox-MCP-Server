# Integration modes

## 1. Studio MCP Compatibility (no Studio required)

This mode is intended for phone-only and cloud development. It exposes a Studio-oriented workflow through APOLO's own tools while operating on files and build artifacts rather than a live Studio process.

Planned capabilities:
- inspect project tree and Rojo mappings
- create/update Luau scripts and ModuleScripts as source files
- generate place hierarchy manifests and supported instance specifications
- create UI layouts and connect them to Luau controllers
- generate procedural map/build manifests
- validate Luau and project structure with installed headless tools
- package project artifacts for upload or manual handoff
- optionally forward compatible actions to an external Studio MCP server when configured

Not equivalent without Studio:
- live Explorer/DataModel inspection
- interactive Play mode and physics/gameplay testing
- Studio plugin execution and editor-only APIs
- visual confirmation of the exact rendered place

When unavailable, these operations must be clearly marked as requiring a Studio runtime or remote test environment.

## 2. Roblox Open Cloud

The Open Cloud adapter will implement only documented endpoints supported by the configured API key and current Roblox API version. Initial capability groups:

- API key validation / permission diagnostics where supported
- experience and place metadata reads
- asset upload and asset operations where supported by the applicable endpoint
- place publishing where supported
- DataStore access where supported
- user/group ownership and target verification where supported

The adapter must maintain an endpoint capability registry instead of assuming all operations are available. API keys are read from `ROBLOX_API_KEY`; they must never be accepted as ordinary tool arguments or written to logs.

## Publish modes

### Manual Creator Dashboard
APOLO produces the package, manifest, hashes, validation report and exact handoff instructions. The user signs in to Creator Dashboard and completes the manual action. APOLO must not claim publication until the user or a verifiable Roblox response confirms it.

### Automatic after user approval
APOLO prepares a release candidate. The user approves the exact experience ID, place ID, artifact hash, version and target. Only then may GitHub Actions call the Open Cloud publishing adapter. Approval must be bound to that immutable release candidate; any changed artifact requires new approval.

No default auto-publish. No publishing from untrusted pull requests. Use protected GitHub environments and required reviewers for production secrets.
