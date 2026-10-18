---
name: roblox-ui
description: Design and build polished, mobile-ready Roblox UI in code — HUDs, menus, shops, inventories, popups, notifications — with theme tokens, scale-based layout, animated feedback, and device testing via the Studio device simulator. Use for any ScreenGui, BillboardGui or SurfaceGui work.
---

# Roblox UI

## Architecture (code-built via Rojo)
- Build UI in client modules (`src/client/UI/<Screen>.luau`) or as `.model.json`; mount under `PlayerGui` from `init.client.luau`. If the project uses StarterGui, add a mapping in `default.project.json`.
- One `Theme.luau` in `src/shared` with tokens: colors (bg, surface, primary, accent, text, muted, success, danger), corner radius, stroke, font (`Enum.Font.GothamBold`/`BuilderSans` or `Font.new(...)`), spacing scale (4/8/12/16/24).
- A tiny `create(className, props, children)` helper keeps UI code readable.
- Screens are state-driven: one `open(name)` / `close(name)` controller so only one modal is open at a time.
- `ScreenGui.ResetOnSpawn = false`, `IgnoreGuiInset` deliberately chosen, `ZIndexBehavior = Sibling`.

## Layout rules
- Size with **Scale**, not Offset; add `UIAspectRatioConstraint` for squares/cards and `UISizeConstraint`/`UITextSizeConstraint` to cap extremes.
- Use `UIListLayout`/`UIGridLayout` + `UIPadding` — never hand-position lists.
- `TextScaled = true` with `UITextSizeConstraint` (MaxTextSize) for readable text on all devices.
- Touch targets >= 44 px on phone; keep the bottom-right clear for mobile jump/thumbstick, top-left for Roblox menu.
- Respect `GuiService:GetGuiInset()` and the top bar.

## Visual polish
- `UICorner` (8-16 px), `UIStroke` (1-3 px, darker shade), `UIGradient` sparingly for depth.
- Consistent iconography (one style); currency icons next to numbers; abbreviate big numbers (1.2K, 3.4M).
- Hierarchy: one primary button per screen in the accent color.
- Motion: open = scale 0.9->1 + fade, `Back` easing 0.2 s; button hover/press = scale 1.05 / 0.95 + click sound; number changes tick up.
- Feedback for every action: toast notifications for rewards/errors, disabled state when unaffordable, red flash on failure.

## Interaction
- Use `Activated` (works for mouse, touch, gamepad) not `MouseButton1Click`.
- Support gamepad selection (`GuiService.SelectedObject`, `Selectable`) for console players.
- UI only sends intent to the server (e.g. `BuyItem(itemId)`); the server validates and replies; the UI updates from server state (attributes/values/remotes), never assumes success.

## Testing
- Use the Studio MCP `skill` `rbx-device-simulator-lua` to switch to phone/tablet/console and `screen_capture` each. Fix overlaps, clipped text, tiny buttons.
- Check: first-time player understands what to do from the HUD alone.
