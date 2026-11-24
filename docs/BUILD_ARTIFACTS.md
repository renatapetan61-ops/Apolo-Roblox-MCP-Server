# Build artifacts and approved publishing

## Build a Roblox place file

The GitHub Actions workflow `.github/workflows/build-place.yml` installs the pinned Rojo CLI 7.7.1 and builds a place file without Roblox Studio.

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
