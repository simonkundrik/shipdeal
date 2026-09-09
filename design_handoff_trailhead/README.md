# Handoff: ShipDeal “Trailhead” — country-specific landed pricing + build visualiser

## Overview
Two features, one UI: (1) replace region buckets with **per-country landed pricing** so the
comparison sorts on what the shopper actually pays at their door, and (2) a **build-page bike
visualiser** that draws a side-profile bike for the chosen riding style, renders each picked part
to its brand, and flags compatibility problems.

## About the design files
The files in `design/` are **design references written in HTML** — a working prototype of the
intended look and behaviour, not production code to paste in. The task is to recreate them in the
ShipDeal codebase — a stdlib http.server app whose pages are assembled as f-strings in app.py,
with one module-level CSS string. The prototype's
JavaScript state model exists only to make the reference interactive; the real implementation is
server-side Python string assembly plus the two fetch helpers app.py already has.

`IMPLEMENTATION.md` is the part that matters for merging: it maps every piece of the design onto
the modules that already exist in this repo (`regions.py`, `landed.py`, `filters.py`, `app.py`),
gives exact function signatures, and calls out where the current landed-cost model is wrong.

## Fidelity
**High fidelity.** Colours, type, spacing, radii and copy below are final. Recreate the UI to match;
do not re-style it with another system.

## Screens / views

### 1. Dashboard / search (app.py `render()`, and `browse_render()` for `/?browse`)
Purpose: pick a delivery country, a component and a style; get product pages sorted by landed cost.

- **Sticky header** — padding 14px 32px, `rgba(242,237,227,.92)` + `backdrop-filter: blur(14px)`.
  Left: wordmark “SHIPDEAL” (Big Shoulders Display 800, 26px, tracking -.02em) + kicker
  “Trail-tested parts index” (Barlow Condensed 700, 11px, tracking .18em, uppercase, clay).
  Right, in order: a right-aligned two-line block — “Delivering to” (Barlow Condensed 700, 12px,
  tracking .14em, uppercase, #4E5A52) over the live tax line (DM Mono 11px, #7A8578) reading
  “20% VAT · prices in GBP · duty-free under £135.00”; the **country select** (pill #F1EADD, no
  border, min-height 44px, Barlow Condensed 700 14px uppercase) with an `<optgroup>` per continent;
  the build chip (pine #16211C pill, “BUILD” + running landed total, DM Mono 15px #F2EDE3).
- **Hero** — full-bleed photo, height `clamp(460px,72vh,660px)`, radius `0 0 34px 34px`, gradient
  `to top, rgba(22,33,28,.9) 0%, rgba(22,33,28,.45) 45%, rgba(22,33,28,.15) 100%`. Kicker
  “New · in stock · landed price for {country}” (Barlow Condensed 700 13px, tracking .24em, #E8B39C).
  H1 “Parts that make it to the trailhead” — Big Shoulders Display 800, `clamp(52px,9vw,132px)`,
  line-height .88, tracking -.025em, #F2EDE3, max-width 16ch. Body Newsreader 400,
  `clamp(17px,1.6vw,21px)`, line-height 1.5, #DCD6C9, max-width 56ch.
- **Gate strip** — #EBE4D8 band, four items (flex 1 1 220px): clay mono number, Barlow Condensed
  700 15px uppercase title, Newsreader 15px #4E5A52 body. Copy: 01 New only / “Used and
  second-hand listings are rejected on the title.” · 02 Stock, with evidence / “We quote the
  phrase that proved it — ‘add to cart’, ‘in stock’.” · 03 The real price / “Authoritative modal
  price. Fees and financing lines thrown out.” · 04 A link that loads / “Direct product page,
  checked live. No homepage redirects.”
- **Search console** — card #FBF8F2, radius 26px, shadow `0 24px 50px -32px rgba(22,33,28,.4)`,
  padding 26px 28px 28px. Row 1: ten component pills (#EFE8DB, radius 999px, Barlow Condensed 700
  14px tracking .1em uppercase, #5A665C, min-height 44px; hover → pine fill, paper text) labelled
  from the `COMPONENTS` keys with underscores as spaces. Row 2: query field (pill #F1EADD, clay
  “/” prefix, Newsreader 19px), style select, wheel select, “In stock only · on/off” toggle (48px
  pills), clay SEARCH button (Big Shoulders 800 20px uppercase, 52px, radius 999px). Row 3: DM Mono
  12px #4E5A52 preset readout from `STYLE_DEFAULTS` + `COMPONENTS` — “{style} preset → fork 170mm
  · rear 170mm · wheel 29in” and “budget band → £300 – £1,400 frame”.
- **Build panel** — see screen 2.
- **Results** — heading “Cheapest first” (Big Shoulders 800 `clamp(26px,3vw,36px)`) + DM Mono 12px
  “{n} genuine product pages · sorted on the landed cost to {country}”. Each row: card #FBF8F2,
  radius 24px, padding 22px, gap 26px, shadow `0 18px 40px -30px rgba(22,33,28,.45)`, flex-wrap.
  Image cell 196×150, #EFE8DB, radius 18px, rank badge top-left (DM Mono 11px, pine 80% pill).
  Middle column: component name (Barlow Condensed 700 13px tracking .16em uppercase, clay) +
  retailer (DM Mono 11px); brand (Big Shoulders 800 27px uppercase); product name (Newsreader
  18px); spec chips (DM Mono 12px — wheel/travel only where `COMPONENTS[c]` flags them True);
  stock badge — in stock `rgba(62,107,68,.15)` bg / #2C5333 text plus the evidence phrase in
  italic Newsreader, unknown `rgba(154,106,18,.17)` / #6F4C0D; delivery line (DM Mono 12px)
  “delivered to {country} in ~{days} days · {duty note}”. Right column: landed total (DM Mono 500,
  30px), clay caption “DELIVERED TO {COUNTRY}”, breakdown (DM Mono 11.5px) e.g. “net £304.91 +
  ship £14.00 + 4.1% duty £12.50 + 20% VAT £66.28 + clearance £12.00”, then “listed €429.00 at
  probikesupply (NL)”; clay “BUY CHEAPEST →” pill (Big Shoulders 800 17px) and “Add to build”
  pill (#EFE8DB). Below the list: hidden-listings notice (#EBE4D8 pill, DM Mono 12.5px) when
  retailers don't deliver there, then the landed-cost caveat paragraph (Newsreader 16px, max 70ch).
- **Kit list** — sticky sidebar (flex 1 1 320px, top 92px), pine #16211C, radius 28px. Rows: 54×46
  thumb (radius 14px), component label, brand + name (Newsreader 16px, ellipsis), landed price
  (DM Mono 13px), × remove. Footer: “Landed in {country}” + total (DM Mono 28px), paper
  “OPEN ALL BUY LINKS” pill, “saved to data/builds.json” caption.
- **Footer** — #EBE4D8 band: “Retailer ring · live scrape” + one pill per `RETAILERS` key.

### 2. Build panel (bike visualiser)
Purpose: show the bike being assembled, which slots are filled, and what is incompatible.
Pine block (radius 34px, padding 32px 34px 20px):
- Header “Your {style} build” (Big Shoulders 800 `clamp(28px,3.2vw,40px)`) + DM Mono readout
  “head angle 64° · fork 170mm · 29in wheels · single-crown”; right: “Installed n/10” chip
  (`rgba(224,118,63,.16)`).
- SVG `viewBox="0 0 1000 630"`, full width, with ten HTML callout labels absolutely positioned
  over it (five left at 2.4%, five right at right 2.4%, width 21%). Label = Barlow Condensed 700
  15px tracking .12em uppercase (“04 · Wheelset”) + DM Mono 12px value (“Hunt · £519.00” or
  “not picked”). Leader starts at the label column's inner edge (SVG x 228 / 772) level with the
  label's top line, 2.6r dot, and ends on a 5r dot at the part anchor. Picked = clay #E0763F with
  an 11r halo; empty = #5F6C62; flagged = #D9634A.
- Compatibility cards under the SVG: `rgba(242,237,227,.05)`, radius 18px, 10px status dot
  (error #D9634A, warn #D8A23C, ok #6FBE7E), Barlow Condensed title + Newsreader detail.

Geometry, brand looks and slot positions are in `reference/bike_geometry.json`; the drawing maths
is described in `IMPLEMENTATION.md` §5.

## Interactions & behaviour
- Country select → re-prices every row and the kit list, re-sorts results, removes and counts
  retailers that don't serve the country, re-words the tax line, hero kicker and captions.
- Component pill toggles the component filter (second click clears).
- Style select → new geometry + preset readout + re-runs the compatibility gate.
- Wheel select, in-stock toggle and query map to `filters.Filters` unchanged.
- “Add to build” fills that component's slot (one per component, replacing); the callout turns
  clay and totals update. “×” in the kit list removes it.
- Hover: pills invert to pine/paper; result cards do not lift; buy pill → pine.
- No entrance animations; transitions where used are 120ms ease.
- Responsive: everything flex-wraps, the kit list drops under the results below ~900px, the SVG
  scales with its box (callouts are %-positioned so they follow).

## State
Server-side, in the query string so links are shareable: `country` (ISO-2, default GB),
`component`, `q`, `brand`, `style`, `wheel`, `travel`, `min`, `max`, `stock`.
Persisted: the build (component → row) via `builds.py`, unchanged. Derived per request: landed
cost per row, hidden-retailer count, compatibility issue list.

## Design tokens
Colour — paper #F2EDE3, paper-2 #EBE4D8, card #FBF8F2, sunken #EFE8DB, input #F1EADD, dust
#D5CBB8, ink #16211C, ink-2 #2C3830, ink-60 #4E5A52, ink-40 #8A8578, clay #B94A26, clay-light
#E0763F, clay-pale #E8B39C, moss #3E6B44 / #2C5333, amber #9A6A12 / #6F4C0D, error #D9634A,
warn #D8A23C, ok #6FBE7E, on-ink #F2EDE3, on-ink muted #9EAA9E / #A9B3A9 / #DCD6C9.
Type — Big Shoulders Display 600/800 (display, uppercase, tracking -.02em, line-height .88–1);
Newsreader 400/500 + italic (body 15–21px, line-height 1.45–1.55); Barlow Condensed 600/700 (UI
labels 11–16px, tracking .1–.24em, uppercase); DM Mono 400/500 (every number, 11–30px).
Spacing — 8px base; band padding 56–72px; card padding 22–28px; gaps 8/12/18/26/32.
Radii — 999px pills, 34px hero/panel, 28px sidebar, 26/24px cards, 18px inner, 14px thumbs.
Shadows — console `0 24px 50px -32px rgba(22,33,28,.4)`, result card
`0 18px 40px -30px rgba(22,33,28,.45)`, kit list `0 28px 60px -36px rgba(22,33,28,.65)`, build
panel `0 34px 70px -40px rgba(22,33,28,.6)`. **No 1px outlines anywhere** — separation is tone
and shadow.

## Assets
Fonts: Google Fonts — Big Shoulders Display, Newsreader, Barlow Condensed, DM Mono.
Photography: none supplied. The prototype uses drop-in placeholders for the hero and every product
image; wire those to real scrape images and one licensed hero shot. No icon set — numbers and type
carry the labelling.

## Files
- `design/shipdeal-trailhead.html` — self-contained interactive reference (open in a browser).
- `design/ShipDeal v2.dc.html` + `design/image-slot.js` — editable source of that reference.
- `design/DESIGN.md` — the design system in nine sections.
- `AGENT_PROMPT.md` — **start here**: what to read in what order, ground rules, definition of done.
- `IMPLEMENTATION.md` — repo-specific port map (read straight after AGENT_PROMPT).
- `reference/countries.py`, `reference/shipping.py`, `reference/landed_v2.py` — drop-in
  reference implementations of the pricing model the design assumes.
- `reference/test_landed_v2.py` — pytest cases pinning the behaviour.
- `reference/bike_geometry.json` — geometry, brand looks and slot table for the visualiser.
