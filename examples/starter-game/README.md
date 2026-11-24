# APOLO Starter Experience

A minimal Rojo project used to validate the repository's headless place build and artifact pipeline.

- Server script creates a baseplate, spawn and discovery platforms.
- Shared ModuleScript contains game configuration.
- Client LocalScript creates a starter HUD.
- The GitHub workflow installs the Rojo CLI; Roblox Studio is not required to build the place file.

Run the APOLO Build Place workflow to create an RBXLX artifact. The build workflow never publishes. Use the separate protected Publish Place workflow only after reviewing the artifact and configuring the roblox-production environment reviewers.
