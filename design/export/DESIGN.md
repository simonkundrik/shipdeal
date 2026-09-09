# DESIGN.md — ShipDeal "Trailhead"

## 1. Visual Theme & Atmosphere
Outdoor-magazine, not gamer-neon. Bone paper canvas, deep pine ink, clay accent, full-bleed
dirt photography. Feels like a well-made trail guide: warm, weathered, confident, quiet in the
margins and loud in the headlines. Density is editorial — generous whitespace, one idea per band.

## 2. Color Palette & Roles
- paper `#F2EDE3` — page canvas
- paper-2 `#E8E1D4` — recessed bands, inputs
- dust `#D5CBB8` — hairlines, borders
- ink `#16211C` — primary text, dark bands
- ink-60 `#4E5A52` — secondary text
- clay `#B94A26` — primary CTA, accent rules, kickers
- moss `#3E6B44` — in-stock
- amber `#9A6A12` — stock unknown
- rust-red `#9E3427` — out of stock / rejected
Max two background colors per screen (paper + ink). Accent is used sparingly: one CTA, one rule.

## 3. Typography Rules
- Display: **Big Shoulders Display** 800, uppercase, tracking -0.02em, line-height 0.9
- Editorial body: **Newsreader** 400/500, 18–20px, line-height 1.55
- UI labels: **Barlow Condensed** 700 uppercase, tracking 0.12em, 12–15px
- Numerals/prices: **DM Mono** 500 — prices are data, always mono
Never set display type below 24px; never set body below 15px.

## 4. Component Stylings
- Buttons: 2px radius (near-square), clay fill / ink text for primary, ink 1px outline for secondary
- Inputs: paper-2 fill, 1px dust border, no shadow, 2px radius
- Cards: paper on paper-2 with 1px dust border, no drop shadows — separation by hairline and space
- Badges: 1px border + 12% tint of the semantic color, uppercase condensed label + evidence phrase
- Photography: full-bleed or hard-edged rectangles, never rounded more than 2px

## 5. Layout Principles
8px spacing base; band padding 72–96px vertical. Max content width 1320px. Editorial two-column
(content + kit list) collapsing to one. Hairline rules separate bands instead of shadows.

## 6. Depth & Elevation
Flat. Depth comes from photography, tonal bands (paper vs ink) and hairlines. No box-shadows.

## 7. Do's and Don'ts
Do: big photography, big type, mono prices, honest badges with evidence text.
Don't: gradients-as-decoration, glows, neon, emoji, rounded pill cards, drop shadows.

## 8. Responsive Behavior
Everything reflows via flex-wrap with generous flex-basis; no fixed widths on text columns.
Hit targets ≥44px. The kit list drops under the gallery below ~900px.

## 9. Agent Prompt Guide
"Add a screen to ShipDeal using the Trailhead system: bone paper canvas, pine ink, clay accent,
Big Shoulders display caps, Newsreader body, DM Mono prices, hairline borders, no shadows."
