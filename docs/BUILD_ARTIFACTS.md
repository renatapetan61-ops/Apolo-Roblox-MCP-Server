# Build artifacts and approved publishing

## Build a Roblox place file

The GitHub Actions workflow `.github/workflows/build-place.yml` downloads the pinned Rojo CLI 7.7.1 Linux binary from the official release, verifies its published SHA-256 checksum, and builds a place file without Roblox Studio.

- Push changes under `examples/starter-game/` to trigger the sample build, or
- Run the APOLO Build Place workflow manually and provide a `.project.json` path that exists inside this repository.

The default example is `examples/starter-game/default.project.json`. The workflow produces exactly one `apolo-place.rbxlx`, a `SHA256SUMS` file and an artifact named `apolo-place-{run_id}`. Artifacts are retained for 14 days. The workflow summary displays the source run ID, artifact name and SHA-256.

The build workflow never uploads the place to Roblox and never publishes it.

## Publish after review

The separate APOLO Publish Place workflow requires:

- The successful source build run ID.
- The artifact name from the build summary.
- The Roblox universe ID and place ID.
- The exact SHA-256 from the build summary.
- The protected GitHub Environment named `roblox-production`.

Configure required reviewers on that environment in repository settings. The workflow downloads only an artifact from this repository, verifies the hash, checks place metadata, submits the current Roblox Assets API update and polls the asynchronous operation. Do not approve a production publish until the artifact and target place have been reviewed.

## Current boundary

The checked-in starter experience is a build-pipeline fixture, not a finished commercial game. The workflow can build another Rojo project committed inside this repository by selecting its project file. It cannot build a project that exists only in a local phone workspace until that project is committed or otherwise supplied to the workflow.


## First successful sample build

On 2026-11-24, the sample workflow completed successfully:

- Source run ID: `45506347168`
- Artifact name: `apolo-place-45506347168`
- File: `apolo-place.rbxlx`
- File SHA-256: `0df412f5e6c58b42c3e434b8a7b55e1f6c6da0d223eee15234c78359e51e4aaf`

This is the starter experience fixture, not a finished game. The artifact expires after the configured 14-day retention period. Rebuild before using the protected publishing workflow if it has expired.
