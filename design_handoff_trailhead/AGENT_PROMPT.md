# START HERE — prompt for the implementing agent

You are implementing a design into an existing Python repo. Read these three files in this order,
then work through the commit list. Do not start coding from the screenshots.

1. `IMPLEMENTATION.md` — how the design maps onto this repo's modules, and what is currently
   wrong in `landed.py`. This is the authority for behaviour.
2. `README.md` — exact layout, colours, type, copy for every element. Authority for visuals.
3. `design/shipdeal-trailhead.html` — open it in a browser and click it. Authority for
   interaction. Its inline styles are the source of truth when the docs and the file disagree;
   its JavaScript is throwaway (the real app renders server-side).

## What this codebase is (do not assume otherwise)
- Plain stdlib `http.server` / `ThreadingHTTPServer` in `app.py`. **No Flask, no Jinja, no
  templates/ directory, no build step, no npm.** Pages are Python f-strings; all CSS is one
  module-level `STYLE` string; fonts come from `FONT_LINK`.
- Rendering entry points: `render(...)` (search page, POST) and `browse_render(components,
  country, rows)` (`/?browse`), with `row_line(row)` per result card.
- Data comes from `populate.py` / `search.py`; prices are already normalised to `price_gbp`
  by `price.py`. Do not re-scrape or re-model the data layer.
- Tests are pytest under `tests/`, importing modules flat (e.g. `from landed import ...`), so
  new modules go in the repo root next to the others.

## Ground rules
- **Add, don't rip out.** `REGIONS`, `RETAILERS`, `COLLECTIONS`, `shipping_hint()` and
  `retailers_for()` still drive the scraper ring. The country model is for *pricing and display*.
  Where a call still needs a region (e.g. `find_cheapest(query, region, ...)`), map country →
  region rather than changing the scraper's contract.
- **Keep the endpoints and their JS.** `/build/add` and `/build/remove` with the existing
  `addToBuild`/`rmFromBuild` fetch helpers and `builds.Pick` shape.
- **The repo's own `design/export/DESIGN.md` is stale** (it describes 1px borders and 2px radii —
  an earlier revision). Use `design/DESIGN.md` from THIS bundle: no outlines, pill controls,
  rounded shadowed cards. If you see a `1px solid var(--dust)` border in the current `STYLE`,
  that is the old design, not a pattern to follow.
- **All money arithmetic in GBP**, converted once at render time by `money(cc, gbp)`. Never store
  or add local-currency figures.
- The reference `*.py` files in `reference/` are drop-in: copy them to the repo root (renaming
  `landed_v2.py` → `landed.py` once the shim is in place) rather than retyping the tables.

## Definition of done
Behaviour (assert these, they are the feature):
- The same listing priced to DE and to SE differs by exactly the VAT ratio 1.25/1.19.
- A GB retailer to a GB shopper returns the listed price unchanged — no VAT added on top.
- An NL retailer to a GB shopper gains duty + 20% VAT + a £12 clearance fee.
- A £42 line from IE to GB pays VAT but no duty (under the £135 threshold).
- A retailer with no postage entry for the destination zone is **dropped and counted**, never
  priced at zero.
- Results are sorted on landed total; the kit-list total is the sum of landed totals.
- Norway/Switzerland/New Zealand headers read “duty from the first NOK/CHF/NZD”, never
  “duty-free under 0 kr”.
Visual:
- No 1px outlines anywhere in `STYLE`; controls are pills; cards are rounded and shadowed.
- The four fonts load and are used in their assigned roles (numbers always DM Mono).
- Layout reflows without horizontal scroll at 1440 / 1024 / 768 / 390 wide.
Tests:
- `reference/test_landed_v2.py` passes (copy it into `tests/`).
- `tests/test_landed.py` and `tests/test_landed_row.py` will need their expected numbers
  updated — the old ones encode the double-taxing bug. Update them deliberately, in the same
  commit as the model change, with a comment saying why.
- Everything else under `tests/` stays green.

## Ask the repo owner before
- Changing the `builds.Pick` schema or `data/builds.json` on-disk format.
- Replacing the stdlib server with a framework.
- Sourcing live FX or real VAT/duty tables (the bundled numbers are deliberate placeholders —
  correct in shape, illustrative in value; wire them to a real source only if asked).
- Adding any dependency (`requirements.txt` is currently one line).

## Suggested first commit
Copy `reference/countries.py` and `reference/shipping.py` to the repo root, copy
`reference/test_landed_v2.py` to `tests/`, and run pytest. It will fail only on the landed
model — which is step 3 in `IMPLEMENTATION.md` §6. That gives you a red-to-green path through
the whole feature.
