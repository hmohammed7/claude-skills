---
name: roblox-launch-marketing
description: Monetize, launch and market a Roblox game — game passes, developer products (correct ProcessReceipt), premium benefits, title/description/thumbnails/icon, sponsored ads, social content, analytics (retention, conversion), events and update cadence, and policy compliance. Use when preparing a release, adding monetization, or growing players.
---

# Roblox monetization, launch and marketing

## Monetization (fair, not pay-to-win)
- **Game passes** (permanent): 2x currency, VIP area, extra slots, cosmetic trails, auto-collect. Check with `MarketplaceService:UserOwnsGamePassAsync` (pcall, cache per player), prompt with `PromptGamePassPurchase`, react to `PromptGamePassPurchaseFinished`.
- **Developer products** (repeatable): currency packs, boosts, revives, skips. Handle in exactly ONE server `ProcessReceipt` callback:
  - Look up the player; if not in game return `NotProcessedYet`.
  - Make it idempotent: record `receiptInfo.PurchaseId` in the player's saved data; if already granted, return `PurchaseGranted`.
  - Grant + save successfully **before** returning `Enum.ProductPurchaseDecision.PurchaseGranted`; on any failure return `NotProcessedYet` so Roblox retries.
- **Premium**: small perks for Premium members (Premium Payouts reward engagement time).
- Price ladder: one cheap impulse item (25-99 R$), a core pass (199-499 R$), a whale item. Show value clearly in the shop UI.
- Paid random items must disclose odds; follow Roblox's paid random item and age-appropriateness policies. Never link off-platform.
- The user creates passes/products in the Creator Dashboard; ask them for the IDs and put them in a `Products.luau` config.

## Store page assets
- **Title**: short, searchable genre keyword + hook ("Brainrot Tycoon", "Escape the ..."). Avoid clickbait the game can't deliver.
- **Icon** 512x512: one bold subject, high contrast, readable at tiny size, no small text.
- **Thumbnails** 1920x1080 (16:9), up to ~10: action moment + character emotion + clear goal; first thumbnail = the hook. Capture scenes with `screen_capture` from staged camera angles (set lighting, pose characters, add VFX), and/or generate concept art if an image tool is available.
- **Description**: first two lines = hook + what you do; then features as bullets, update log, social/group link (Roblox group only).
- Fill the Experience Questionnaire (maturity rating) honestly; set genre and supported devices.

## Launch checklist
1. QA loop passed (`roblox-qa-loop`), tested on phone, tablet, PC.
2. DataStores tested with API access enabled in a private place; BindToClose saves.
3. Analytics events in key funnel steps (`AnalyticsService` custom/funnel/economy events): join -> tutorial done -> first upgrade -> first purchase.
4. Private test with friends; fix the top 5 confusions.
5. Publish; set icon/thumbnails/description; create a Roblox group for the game.
6. Small sponsored/ads budget first (Ads Manager), compare thumbnails by click-through rate, then scale the winner.

## Growth loop
- Key metrics in the Creator Dashboard: D1 retention (aim 25%+), D7 (8%+), average session length, payer conversion, ARPDAU, thumbnail CTR.
- Update weekly early on: new content + an event; post the update log in the description and group.
- Social: short vertical clips (TikTok/YouTube Shorts) of the most satisfying moment; use `content-engine` / `marketing-campaign` skills for scripts and calendars.
- Retention hooks: daily rewards with streaks, limited-time events, friend invite bonus (`SocialService:PromptGameInvite`), group join reward, leaderboards.
- Use `market-research` / `competitive-platform-analysis` to study top games in the genre before deciding features or prices.
