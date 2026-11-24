# Security and release policy

- Keep `ROBLOX_API_KEY` and asset-provider keys in GitHub Actions Secrets or a protected runtime environment.
- Use the narrowest Creator Dashboard API scopes possible. Do not use account cookies or browser session tokens.
- Never log secrets or return them from an MCP tool.
- Treat generated files, prompts, model outputs and repository content as untrusted input.
- Restrict project paths to the configured workspace.
- Validate artifact extension, target Universe ID, Place ID and SHA-256 before publishing.
- Automatic publishing must be protected by the GitHub Environment `roblox-production` with required reviewers configured in repository settings.
- The workflow's `release_sha256` input binds the reviewer-approved workflow dispatch to the exact downloaded artifact. Any changed artifact requires a new dispatch and approval.
- Do not allow pull requests from forks to access production secrets.
- Do not claim a place is live solely because an upload request was accepted; record and verify the Roblox response/version.
- Revoke keys that may have been exposed and rotate them immediately.


## Direct MCP publication

Direct publication through the MCP tool is disabled by default. The safer recommended path is the `roblox-production` GitHub Environment with required reviewers, immutable artifact SHA-256 verification, and Roblox operation polling. Release candidates in the current MCP server process are in-memory and are lost on restart. Do not enable `APOLO_ALLOW_DIRECT_PUBLISH=true` in shared or unattended environments; if enabled for a controlled local session, the operator remains responsible for reviewing the exact target and release hash.

## World materialization and place saving

- Headless world materialization is disabled until `APOLO_ALLOW_LUAU_EXECUTION=true` and each call explicitly confirms execution.
- Saving is a separate opt-in: `APOLO_ALLOW_PLACE_SAVE=true`, `save_place=true` and `confirm_save_place=true` are all required.
- Save operations use `SaveWithoutPublish=true`, but they still overwrite the saved state of the target place. Use a dedicated test place and verify rollback before enabling this flag.
- Roblox may reject SavePlaceAsync unless the place was created with CreatePlaceAsync or has the relevant API enabled in its place settings.

## Roblox asset uploads

- Uploading assets is disabled by default and requires both `APOLO_ALLOW_ASSET_UPLOAD=true` and `confirm_upload=true` for each MCP call.
- Source files must be inside the configured project workspace. Uploads are limited to one file up to 20 MiB and the API-supported extensions documented by Roblox.
- Use a least-privilege API key with asset write permissions. Poll the returned operation and do not assume an asset is ready until Roblox reports `done=true` and returns the asset result.
- Uploading an asset is not the same as adding it to a game, publishing an experience, or generating a new asset with AI.
