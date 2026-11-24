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

## 3. Headless Roblox Luau Execution (Open Cloud)

Roblox now provides a stable Open Cloud Luau Execution API. APOLO exposes it through:

- `apolo_execute_luau` — submit a script to a Roblox place task.
- `apolo_get_luau_task` — retrieve task state and return values.
- `apolo_get_luau_task_logs` — retrieve print output.

Required key scopes: `universe.place.luau-execution-session:write` to create tasks and the corresponding read scope to inspect tasks/logs. Enable `APOLO_ALLOW_LUAU_EXECUTION=true` only in a controlled environment and set `confirm_live_execution=true` for each call.

Important engine constraints from Roblox:
- A task runs against a specific place version and can run up to five minutes.
- Physics simulation does not run; server and LocalScripts in the place do not automatically run.
- DataModel edits are local to the task and are not automatically persisted.
- Luau scripts can still call cloud services such as DataStores, so treat execution as privileged and test with a non-production universe.
- Maximum ten incomplete tasks per place; Roblox rate limits task creation.

This gives APOLO a genuine Studio-free engine execution path for scripted checks and procedural analysis. It does not replace full interactive playtesting or guarantee that a live multiplayer session behaves correctly.

## Roblox Open Cloud asset uploads

APOLO provides an initial multipart upload adapter through `apolo_upload_asset` and `apolo_get_asset_operation`. Supported upload categories and formats are constrained by the Roblox Assets API. Upload requires a source file in the project workspace, a creator user/group ID, `APOLO_ALLOW_ASSET_UPLOAD=true`, and `confirm_upload=true`. The API is asynchronous; poll the returned operation before using the resulting asset ID. See [Roblox asset usage guide](https://create.roblox.com/docs/cloud/guides/usage-assets).

## DataStore APIs

The Open Cloud adapter supports listing standard DataStores, listing entries, reading one entry and updating an existing entry. Configure the matching API key scopes: `universe-datastores.control:list`, `universe-datastores.objects:list`, `universe-datastores.objects:read`, and `universe-datastores.objects:update`. Writes require `APOLO_ALLOW_DATASTORE_WRITES=true` and `confirm_update=true`. Create/delete operations are not exposed yet. See [Roblox's Open Cloud DataStore guide](https://create.roblox.com/docs/cloud/guides/data-stores) and [scope reference](https://create.roblox.com/docs/cloud/reference/scopes).
