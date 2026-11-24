# World materialization

The `apolo_materialize_world` MCP tool creates Roblox instances inside a headless Open Cloud Luau Execution task.

## Supported scene inputs

- BaseParts: `Part`, `SpawnLocation`, `WedgePart`, `TrussPart`
- Grouped Models using the optional `group` field
- Terrain blocks using Roblox `Terrain:FillBlock`
- Lighting: clock time, brightness, global shadows, ambient and outdoor ambient colors
- Part position, size, rotation, color, material, anchoring, collision and transparency

The generator validates and bounds all values. It does not accept arbitrary Luau snippets as scene definitions. It currently does not generate arbitrary meshes, CSG, detailed imported models, textures, clothes, animations or audio.

## Safe execution

The server must have `ROBLOX_API_KEY` and the required Open Cloud Luau Execution scopes. Cloud execution is disabled by default. For a controlled test session, set:

```dotenv
APOLO_ALLOW_LUAU_EXECUTION=true
APOLO_ALLOW_PLACE_SAVE=false
```

Then call `apolo_select_integration("open_cloud")` and `apolo_materialize_world` with `confirm_live_execution=true`. Poll the returned task using `apolo_get_luau_task` and `apolo_get_luau_task_logs`.

## Saving the generated place

By default, the scene exists only inside the execution task and is not persisted. Saving is a separate destructive operation because it overwrites the saved state of the target place. It is disabled by default and requires all three:

1. A dedicated test place, not the production place.
2. `APOLO_ALLOW_PLACE_SAVE=true` in the server environment.
3. Both `save_place=true` and `confirm_save_place=true` in the tool call.

The generated Luau uses `AssetService:SavePlaceAsync({PlaceId = game.PlaceId, SaveWithoutPublish = true})`. This does not publish the place. Roblox documents that SavePlaceAsync only works for places created with CreatePlaceAsync or places where the API has been enabled in place settings. If the platform rejects the save, the task result contains the error; APOLO must not report the scene as persisted.

Do not enable saving until the test place, Open Cloud permissions and rollback procedure are verified. Physics simulation and normal server/client script startup are not part of Luau Execution.
