# ShipDeal — "Trailhead" web design

Drop-in front-end design for ShipDeal. Nothing here changes the Flask app; it is the
target UI to build `app.py`'s templates toward.

## Files
- `shipdeal-trailhead.html` — the full design, self-contained (fonts + runtime inlined).
  Opens offline in any browser. Interactive: country selector, component filters,
  add/remove parts, live bike diagram, compatibility flags.
- `DESIGN.md` — the design system (palette, type scale, component rules, do/don't).
- `ShipDeal v2.dc.html` + `image-slot.js` — the editable source of the design.

## What the design adds over the current UI
1. **Country-specific landed pricing.** Replaces `regions.py`'s EU/UK · US · AU · Global
   buckets with 17 countries. Per country: VAT/GST rate, import duty rate, de-minimis
   threshold, customs clearance fee, currency + FX. Per retailer: origin country, VAT
   regime, per-zone shipping cost, free-shipping threshold, lead time.
   Listed price -> origin VAT stripped -> destination VAT applied (EU OSS) -> duty and
   clearance when the parcel crosses a customs border and clears de-minimis.
   Result: a German listing is not a Swedish price. Sorting is on landed cost, not list price.
2. **Build visualiser.** Side-profile bike drawn from real mm geometry per riding style
   (head angle, fork travel, wheelbase, seat height, dual-crown for DH, motor for e-bike).
   Picked parts render to brand (fork colourways, tyre knob density, rim depth, rotor
   diameter, cassette count); unpicked parts stay dashed ghosts. Callouts label each slot.
3. **Compatibility gate.** Wheel-size clashes, fork travel vs frame/preset, front/rear
   travel mismatch, unconfirmed stock, retailers that will not deliver to the chosen
   country, and duty exposure — flagged under the diagram and on the offending callout.

## Suggested repo integration
- `regions.py`: move from region groups to ISO country codes; add vat, duty, de_minimis,
  clearance_fee, currency, fx.
- new `landed.py`: the landed-cost function (net -> ship -> duty -> tax -> clearance).
- `catalogue.py`: add retailer origin + shipping zones table.
- `app.py`: sort results on landed cost; pass country instead of region.
- `templates/`: port markup from `shipdeal-trailhead.html`.

Fonts: Big Shoulders Display (display), Newsreader (body), Barlow Condensed (UI labels),
DM Mono (prices). All from Google Fonts.
