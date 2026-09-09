# Implementation map — ShipDeal repo (simonkundrik/shipdeal, master)

Read this before merging. Written against the modules that exist today.

## 0. Why the current landed.py gives wrong numbers

`landed_cost()` applies the destination VAT to a price that **already contains the origin
country's VAT**, and it has no notion of where the retailer ships **from**. Consequences:

| case | today | should be |
| --- | --- | --- |
| huntbikewheels (GB) → GB | £519 + 0% = £519 (right, by luck) | £519, VAT already in |
| probikesupply (NL) → DE | NL price + 19% again = double tax | strip 21% NL, add 19% DE |
| probikesupply (NL) → SE | identical to DE | strip 21% NL, add 25% SE (OSS) — the whole point |
| icancycling (CN) → DE | no duty (duty_rate 0.0) | 4.7% duty + 19% VAT + clearance |
| winspace (CN) → GB | no duty | 4.1% duty + 20% VAT + £12 clearance |

Also `COUNTRY_INFO["fx"]` is local→GBP (EUR 0.85) while `landed_cost()` multiplies the list
price by it — FX is being used in the wrong role. In the design FX is **display only**: all
arithmetic is in GBP (`price_gbp` from `price.py`), converted once for rendering. Keep one
direction and name it `gbp_to_local` (so 1/0.85 for EUR).

## 1. regions.py — add origin + zones, keep the region ring

Do **not** delete `REGIONS` / `RETAILERS` / `COLLECTIONS` — the scraper ring still uses them.
Add two tables and move `COUNTRY_INFO` out to `countries.py` (see `reference/countries.py`):

1. `ORIGIN` per retailer: `{"country": "NL", "customs": "EU", "vat_rate": 0.21}`, where
   `customs` is one of UK EU CH NO US CA AU NZ CN. Values in `reference/shipping.py`.
2. `ZONE_POSTAGE` per retailer keyed by **zone** (UK EU EUX NA OC) with
   `{"cost_gbp", "free_over_gbp", "days"}`. A missing zone means *this retailer does not deliver
   there*: drop the row and count it, never price it at zero. `delivery_cost_gbp()` keeps its
   shape but takes a zone (map country → zone with `countries.zone_of(cc)`).

`shipping_hint()` stays for scrape-time notes; the UI no longer prints it — the delivery line is
computed: “delivered to Germany in ~3 days · import duty + 19% VAT applied”.

## 2. countries.py (new) — the 17-country table

`reference/countries.py` is drop-in. Per country: name, group, currency, symbol, symbol_after,
decimals, gbp_to_local, vat_rate, duty_rate, customs, zone, clearance_fee_gbp, duty_free_gbp,
tax_free_gbp. Helpers: `country_info(cc)`, `zone_of(cc)`, `groups()` (ordered continent →
[(cc, name)] for the optgroups), `money(cc, gbp)` (£1,185.39 · 706 kr · CHF 81.87) and
`tax_line(cc)` (header caption — must read “duty from the first NOK” when duty_free_gbp is 0,
never “duty-free under 0 kr”).

Keep `tests/test_countries.py` green: if it asserts on `regions.COUNTRY_INFO`, re-point it at
`countries.COUNTRY_INFO` and rename the fx key in the same commit.

## 3. landed.py — replace with the origin-aware model

`reference/landed_v2.py` mirrors the design exactly:

```python
landed(list_gbp, retailer, country) -> dict
# {"serves", "total_gbp", "net", "ship", "duty", "vat", "clearance",
#  "crossing", "dutiable", "days", "origin", "breakdown", "duty_note", "label"}
```

Order of operations — this is the contract the UI copy describes:

```
net       = list_gbp                        if domestic
          = list_gbp / (1 + origin_vat)     otherwise
ship      = zone cost, 0 above free_over_gbp; None -> row not served
duty      = net * duty_rate                 if crossing and net + ship > duty_free_gbp
vat       = (net+ship+duty) * vat_rate      if not domestic and (not crossing or net+ship > tax_free_gbp)
clearance = clearance_fee_gbp               if duty applied
total     = net + ship + duty + vat + clearance
```

- *domestic* = retailer customs area == destination customs area **and** that area is not EU.
- *intra-EU* (both EU) is deliberately **not** domestic: strip origin VAT, apply destination VAT
  (OSS). That is why a German listing is not a Swedish price.
- *crossing* = customs areas differ.
- `breakdown` is the rendered string (“net £304.91 + ship £14.00 + 4.1% duty £12.50 + 20% VAT
  £66.28 + clearance £12.00”); `duty_note` is the delivery-line tail (“no border to cross” /
  “under the £135.00 duty threshold” / “no duty on this line” / “import duty + 20% VAT applied”).

Keep a `landed_row()` shim so `tests/test_landed_row.py` and existing callers keep working;
`reference/test_landed_v2.py` adds the new cases.

## 4. app.py — where the HTML actually lives

There is **no Flask and no Jinja**: app.py is a stdlib `ThreadingHTTPServer` and every page is
assembled in f-strings. The three things to change:

- `STYLE` (module-level CSS string) — replace wholesale with the Trailhead tokens. The version
  in master is the **pre-revision** design (1px `--dust` borders, 2px radii, no shadows); the
  final design has **no outlines**, pill controls (radius 999px) and soft shadows. Take the values
  from `design/DESIGN.md` in this bundle, not from the repo's current copy.
- `render(...)` (the search page, POST-driven) — rebuild the markup: sticky header with the
  country select, hero, gate strip, search console, results, kit list, footer.
- `browse_render(components, country, rows)` — already country-aware; it is the closest thing
  to the design and the right place to land the new pricing first. `row_line(row)` becomes the
  result card.

Keep as-is: `esc()`, `parse_filters()`, the `Handler` class, and the `/build/add` ·
`/build/remove` endpoints with their `addToBuild`/`rmFromBuild` fetch helpers.

Route contract:

- `do_GET` already reads `country` for the browse page — do the same on the search page and
  drop `region` from the POST form (`countries.REGION_ALIAS` keeps old links working). Note
  `find_cheapest(query, region, ...)` and `retailers_for(region)` still speak regions: map
  country → region for the scrape ring, country for the pricing.
- After `filters.apply`, map each row through `landed()`; rows with `serves is False` go into
  a `hidden` counter; **sort on total_gbp**, not price_gbp (`sort=brand` stays available).
- Pass per row: `landed_label`, `breakdown`, `duty_note`, `days`, `origin`,
  `listed_label` (“listed €429.00 at probikesupply (NL)”), plus today's fields. Spec chips render
  only where `COMPONENTS[row["component"]]` flags wheel/travel True.
- Build totals: `builds.total(picks)` sums `price_gbp`/`total_gbp` — store the landed figure
  in the `Pick` (the `gbp` form field already feeds `total_gbp`) and format with `money()`.
  Never show a raw sum of list prices.
- Existing call site to update: `browse_render` does `r.setdefault("landed_gbp", landed_row(r, info))`
  with an `info` dict; the new `landed_row(row, country)` takes the country code and reads the
  retailer off the row. Update both the call and `row_line()`'s labels.
- Compatibility gate (new `compat.py`); each issue is
  `{"level": "error"|"warn"|"ok", "title", "detail", "keys": [component keys]}`:
  1. **error** wheel sizes differ across frame/fork/wheelset/tires;
  2. **warn** the single wheel size ≠ `STYLE_DEFAULTS[style]["wheel"]`;
  3. fork travel vs preset — **warn** more than 20mm out, **error** more than 40mm over;
  4. **warn** fork travel vs frame rear travel more than 20mm apart;
  5. **warn** any pick whose stock is not in_stock (name the brands);
  6. **error** any pick whose retailer does not serve the country;
  7. **warn** any pick that is dutiable (name the retailers and the VAT rate);
  8. **ok** “No conflicts” only when the build is non-empty and 1–7 are clear.
  `keys` drives the callout colour (#D9634A) in the build panel.

## 5. Build visualiser — porting the drawing

All numbers live in `reference/bike_geometry.json`. `geo_mm` is per style in **millimetres**
(tire radius, ha head angle, travel, wb wheelbase, seat_tube, post, dual, motor). Projection into
the 0 0 1000 630 viewBox: S = 0.2865 px/mm, ground line y = 470,
`x(mm) = ox + mm*S` with `ox = tire*S + (1000 - wb*S - 2*tire*S)/2`, `y(mm) = 470 - mm*S`.

Fixed points (mm): rear axle (0, tire), front axle (wb, tire), BB (434, 345). Fork axis unit
vector u = (-cos(ha), sin(ha)); axle-to-crown = travel + 380; crown = front_axle + u*len; head
tube crown + u*14 → crown + u*150; stem + u*55; bar = stem + (60, 6). Seat axis at 76°:
seat_top = bb + s*seat_tube, saddle = seat_top + s*post; shock from 0.45·seat_tube up the seat
axis to (bb_x*0.5, tire*0.6); rocker = ss_top + (78, -34); crank arm to bb + (152, -92).

Tubes are quads: offset each end by ±width/2 along the segment normal (widths in tube_widths_mm).
Wheels: tyre casing is a stroke cw wide at r = tire - cw/2, tread ticks knob per revolution, rim
at tire - cw - 5, 18 spokes, 11r hub.

`look` maps a picked brand to its rendering: fork stanchion/lower colours, tyre knob count and
casing width, rim colour, rotor diameter, cassette cog count, pedal plate width. Unpicked parts
draw fill none, stroke #5C6A61, stroke-dasharray 6 5, opacity .7 — the ghost state.

`slots` gives each callout its number, label, side and ty in viewBox units; label boxes are
top (ty-20)/630 of the wrapper, width 21%, 2.4% in from their side; the leader runs from x 228
(left) or 772 (right) at y = ty-2 to the part anchor (anchors listed in the JSON).

Put it in a new `bike.py` as a pure function `bike_svg(style, picks) -> str` and interpolate the
string into the page f-string, the same way `row_line()` is used today. No JS is required for the
diagram; the callout labels are absolutely-positioned HTML siblings of the SVG.

## 6. Suggested commit order
1. `countries.py` + money/tax_line + tests.
2. `regions.py`: ORIGIN, ZONE_POSTAGE, zone-aware delivery_cost_gbp.
3. `landed.py` v2 + shim + tests (expect test_landed.py numbers to move — they were wrong).
4. `app.py`: country param, landed sort, hidden count, row fields.
5. `STYLE` + `render()`/`browse_render()`/`row_line()` markup per README.md.
6. `compat.py` + build panel.
7. `bike.py` + SVG.
