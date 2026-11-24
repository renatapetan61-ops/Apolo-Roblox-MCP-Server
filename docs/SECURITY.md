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
