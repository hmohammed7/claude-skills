---
name: rojo
description: Use for any Roblox game or Luau work in a Rojo project (a folder with default.project.json). Covers file layout, file naming, syncing, Luau best practices, and how to combine Rojo with the Roblox Studio MCP tools to build, playtest, and debug games.
---

# Roblox + Rojo workflow

## Golden rules
- Code lives in files on disk. Write and edit scripts as files under `src/`. Never create or edit scripts directly in Studio via MCP (`multi_edit`, `execute_luau` setting `.Source`) — Rojo overwrites Studio with the files.
- Use Roblox Studio MCP for things that are NOT synced code: building/inspecting parts and models in Workspace, inserting assets, playtesting, reading console output, screenshots.
- Assume `rojo serve` is running and Studio is connected (Plugins > Rojo > Connect). If file changes don't show up in Studio (check with `search_game_tree` / `script_read`), ask the user to check the Rojo connection.
- Instances that must persist and are not code (maps, models, UI built in Studio) live in the place file. Tell the user to save the place in Studio after MCP builds them, or define them in `*.model.json` / `default.project.json` if they should be in source control.

## File layout
Always read `default.project.json` first and follow its mapping. The default template is:
- `src/server/`  -> ServerScriptService.Server
- `src/client/`  -> StarterPlayer.StarterPlayerScripts.Client
- `src/shared/`  -> ReplicatedStorage.Shared
To add a new mapping (e.g. StarterGui, ServerStorage), edit `default.project.json`; Rojo picks it up live.

## File naming -> instance type
- `Name.server.luau` -> Script
- `Name.client.luau` -> LocalScript
- `Name.luau` -> ModuleScript
- Folder containing `init.luau` / `init.server.luau` / `init.client.luau` -> the folder itself becomes that script, children become its children
- `Name.model.json` -> instances described in JSON
- `Name.meta.json` / `init.meta.json` -> properties/className for a script or folder
- `Name.txt` -> StringValue, `Name.json` -> ModuleScript returning the data

## Luau style
- Start every file with `--!strict` and use type annotations; export types from modules.
- Use `task.wait`, `task.spawn`, `task.delay`, `task.defer` — never `wait`, `spawn`, `delay`.
- Get services with `game:GetService("...")` at the top of the file.
- Require shared modules via `ReplicatedStorage.Shared.ModuleName`.
- Use `WaitForChild` on the client for replicated instances; not needed on the server for things you created.
- Disconnect connections and `:Destroy()` instances you create; clean up per-player state on `PlayerRemoving`.

## Architecture
- One ModuleScript per system (e.g. `CombatService`, `DataService`, `ShopController`), started by a small bootstrap (`init.server.luau` / `init.client.luau`).
- Server is authoritative: the client only sends intent. Validate every RemoteEvent/RemoteFunction argument (types, ranges, cooldowns, distance) on the server. Never trust the client for currency, damage, or position.
- Keep remotes in one place (e.g. a `Remotes` folder created by the server or defined in `default.project.json`).
- DataStores: wrap calls in `pcall` with retries, use `UpdateAsync`, save on `PlayerRemoving` and `game:BindToClose`, and keep a default data template with version field.

## Workflow for a new game or feature
1. Write a short plan first: core loop, systems/modules, remotes, saved data, UI.
2. Implement code as files in `src/`.
3. Build world/assets with MCP (`execute_luau` for procedural building, `insert_asset` / `search_asset` for toolbox assets, `generate_*` tools for meshes/materials/textures).
4. Verify (below). Iterate until there are no errors.

## Verify loop (after every meaningful change)
1. Save files; give Rojo a moment to sync. Confirm with `script_read` or `search_game_tree` if unsure.
2. `start_stop_play` to start a playtest.
3. `get_console_output` — fix every error and warning in the source files.
4. For visual or gameplay checks use `screen_capture`, and `character_navigation` / `user_keyboard_input` to test interactions.
5. Stop the playtest with `start_stop_play`. Repeat until clean.

## Game feel / quality bar
- Every player action gets feedback: sound, TweenService animation, particles or UI response.
- Clean, readable UI: use UIListLayout/UIPadding/UICorner/UIStroke, scale-based sizing, test on small screens.
- Add onboarding (first-time hint), a clear goal, and progression (leaderstats, unlocks, upgrades).
- Performance: avoid per-frame loops on the server where events work; anchor static parts; use CollectionService tags for repeated behaviors.
