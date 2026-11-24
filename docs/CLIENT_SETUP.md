# Connect AI clients

The MCP server currently supports stdio by default. Install the repository in a Python 3.11+ environment and use an absolute workspace path.

## Install

```bash
git clone https://github.com/renatapetan61-ops/Apolo-Roblox-MCP-Server.git
cd Apolo-Roblox-MCP-Server
python -m venv .venv
. .venv/bin/activate
pip install -e .
```

Set `APOLO_WORKSPACE` to a writable directory. For Open Cloud publishing, set `ROBLOX_API_KEY`, `ROBLOX_UNIVERSE_ID` and `ROBLOX_PLACE_ID` in the process environment. Do not put secrets in MCP arguments or repository files.

## Claude Code

Use the local executable as a stdio MCP server:

```bash
claude mcp add apolo-roblox -- /absolute/path/to/Apolo-Roblox-MCP-Server/.venv/bin/apolo-roblox-mcp
```

## Codex

Add an MCP server entry to the Codex configuration (or use the corresponding `codex mcp add` command supported by your installed Codex version):

```toml
[mcp_servers.apolo-roblox]
command = "/absolute/path/to/Apolo-Roblox-MCP-Server/.venv/bin/apolo-roblox-mcp"
args = []
```

## OpenCode

Add the local command to the OpenCode MCP configuration using the MCP stdio server format supported by your installed OpenCode version:

```json
{
  "mcp": {
    "apolo-roblox": {
      "type": "local",
      "command": ["/absolute/path/to/Apolo-Roblox-MCP-Server/.venv/bin/apolo-roblox-mcp"],
      "enabled": true
    }
  }
}
```

Check the current configuration schema for the client version in use; client config formats can change.

## First commands

1. Call `apolo_server_info`.
2. Call `apolo_list_capabilities`.
3. Call `apolo_select_integration` with `studio_compat` to create source projects, or `open_cloud` for cloud publishing.
4. In Studio compatibility mode, call `apolo_create_project`, then `apolo_write_project_file`.
5. For cloud publication, prepare a reviewed `.rbxl` or `.rbxlx` release with `apolo_prepare_publish`. Inspect the returned target and SHA-256. Only then call `apolo_publish_approved` with the exact approval phrase.

The server process must have the configured environment variables. Restart the MCP client after changing environment variables.
