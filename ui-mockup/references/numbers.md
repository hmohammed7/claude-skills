# UI numbers from tutorials

Values and techniques pulled from tutorials, with where they came from. Read this when choosing a
style (`styles/*.json`), or when a mockup looks flat and you want concrete numbers to try.
**Said** = spoken in the video. **Shown** = only visible on screen (read off a frame).

## Make Your Roblox UI Look 10x Better

- Creator: Develuper (YouTube), uploaded 2026-08-21, 7:03
- Link: https://youtu.be/F6AtQKo3uIY
- Processed: 2026-10-18 (transcript via Whisper "small", values read from 720p frames)
- Built in Figma, then exported as images to Roblox. The button is designed at about 565x139
  Figma px, so the ratio column is what transfers to other sizes (ratios are my arithmetic, not the video's).

### Button style

| What | Technique or value | Ratio to button height | Timestamp | Said / Shown |
|---|---|---|---|---|
| Two goals for every element | Identity (colours, shapes, font, texture) plus depth (looks like a raised 3D button) | - | 1:11 | Said |
| Corner radius | Slightly rounded: 17 on a 139-tall button | ~12% | 1:38-1:52 | Said (slightly rounded), Shown (17) |
| Fill | Vertical gradient of saturated colours, brightest at the top | - | 1:48 | Said |
| Gradient colours | Yellow #FFD900 at the top to orange #FF8000 at the bottom | - | 1:52 | Shown |
| Depth | Copy the shape, move it straight down behind the original, make it a bit darker, then merge them | - | 2:01-2:16 | Said |
| Depth offset | 16 down (button 139 tall, 155 once merged) | ~11.5% | 2:10-2:24 | Shown |
| Depth colour | Dark burnt orange, about #A65300 / #AA5000 | - | 2:24, 4:23 | Shown |
| Outline | Black stroke on the merged shape, set to Outside | - | 2:18-2:22 | Said |
| Outline weight | 4.5 | ~3% | 2:40, 4:23 | Shown |
| Font | Fredoka One, called the classic Roblox font | - | 2:33 | Said |
| Text size | 70 (black depth copy) and 69 (white top copy) on a 139-tall button | ~50% | 2:35-2:40 | Shown |
| Text style | White text, thick black outline, plus the same move-down depth copy | - | 2:37 | Said |
| Text outline | Black, Outside, weight 4.5 | ~3% | 2:40 | Shown |
| Icon | One strong icon is the focus of the button; recolour it as an SVG (vectorise it if it isn't one), give it the same depth | - | 2:43-3:16 | Said |
| Shine | Shapes inside an invisible clipping frame (a mask) with a blend mode, so they stay inside the button | - | 3:23-3:46 | Said |
| Shine blend mode | Tried Multiply, Colour burn and Lighten, settled on Soft light | - | 3:45-3:48 | Shown |
| Edge highlight | Invisible frame the same shape as the button, white Inside stroke, blend mode on; called a small detail with a big payoff | - | 3:52-4:05 | Said |
| Edge highlight values | White, Inside, weight 4, blend mode Colour dodge, corner radius 15-19 | stroke ~3% | 4:03-4:06 | Shown |
| Sparkles | Small star images inside the mask, blend mode Colour dodge | - | 4:08-4:19 | Said (technique), Shown (blend mode) |
| Drop shadow | Optional | - | 4:22 | Said |
| Drop shadow values | X 0, Y 6, blur 4, spread 0, black at 25% | Y ~4% | 4:24-4:26 | Shown |

### Screen layout (shop)

| What | Technique or value | Timestamp | Said / Shown |
|---|---|---|---|
| What makes a screen work | Contrast between buttons, the right colours, a structure that works | 5:03 | Said |
| Structure | A standout top bar that opens the shop | 5:11 | Said |
| Panel background | White with small details, or semi-transparent black, so the other colours have room | 5:18 | Said |
| Item order | Main item bigger, more prominent and first; smaller, less flashy items after it | 5:28 | Said |
| Item card contents | Name, a short description if it bundles several things, a large item image, a green price button | 5:39 | Said |
| Price buttons | Green, the colour people read as money | 5:49 | Said |
| Currency icon | A small currency icon (Robux, coin) next to every price | 5:53 | Said |
| Look of the finished shop | White panel with a light grey inner border, black outlines on everything, red/magenta Close, green STORE and price buttons | 5:20, 6:15 | Shown |

### Getting it into Roblox

| What | Technique or value | Timestamp | Said / Shown |
|---|---|---|---|
| Export | Export each piece as its own image; keep detailed ones as big as possible but under 1024 px, since Roblox scales bigger images down | 6:12 | Said |
| Upload | Upload through Asset Manager to get IDs, then rebuild with ImageLabels and ImageButtons | 6:26-6:39 | Said |
| Sharpness | The creator found the in-game result a little less sharp than in Figma | 6:49 | Said |

### Couldn't read clearly

- **Depth colour:** reads #A65300 at 2:24 and #AA5000 at 4:23. The frames are blurry, so it's one of the two. The depth layer looks redder (closer to #FF5A00) at 2:10, which may be before its colour was changed.
- **Shine blend mode:** Soft light was the last option highlighted before the menu closed, but the frame after doesn't show the chosen value.
- **Edge-highlight corner radius:** 19 at 4:03, then being typed as 15 at 4:04. The final value isn't shown.
- **Text sizes:** the top copy reads 69 but could be 68.
- **Gradient top colour:** #FFD900, though it could be #FFD800.
