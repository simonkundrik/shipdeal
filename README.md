# ShipDeal

**ShipDeal** — search bike parts that **deliver to your region**, at the **cheapest price**.

You pick your region and a part; ShipDeal hunts retailers that ship there, filters to NEW,
in-stock products with working direct buy links, and surfaces the cheapest option with a
picture. Same honesty gate as the MTB build tool: no used/second-hand, no dead links, no
generic search junk — only genuine product pages you can actually buy.

## Why

Bike builders (enduro/DH/XC/e-bike) waste money buying from retailers that don't ship to
their country, or from marketplaces where the "cheapest" listing is used, out of stock, or a
redirect. ShipDeal answers: "what's the cheapest NEW part that actually delivers to me?"

## Features

- **Region-aware search** — choose your delivery region (EU/UK, US, AU, Global); ShipDeal
  prefers retailers known to ship there and flags shipping caveats.
- **Curated build catalogue** — 10 MTB components (frame, fork, rear shock, wheelset, tires,
  drivetrain, brakes, cockpit, pedals, saddle) with credible brands, budgets, and wheel/travel
  style defaults (XC / enduro / freeride / downhill / e-bike).
- **Multi-store scraping** — searches across a ring of live-scrapable retailers
  (probikesupply, CRC, Hunt, Box, ICAN, Winspace, Yoeleo, AliExpress) with a scrapable flag.
- **Product database** — `populate.py` fills `data/products.json` across the catalogue; every
  row carries the authoritative price **plus delivery** (`shipping_gbp` + `total_gbp`), so the
  cheapest-retailer ranking includes shipping (delivery unknown flagged, never silently free).
- **Browse catalogue** — `?browse=<component>&region=…` lists products per component sorted by
  delivery-inclusive total; "Add to build" stores the delivery-inclusive total so the My Build
  grand total is the real delivered price.
- **Stock checker (critical)** — forks must be confirmed IN STOCK (decisive
  "in stock"/"add to cart" wins over Amazon boilerplate); other parts reject only confirmed
  out-of-stock, flagging "unknown" honestly.
- **Exact prices** — every listing price is the authoritative modal price (fee / financing /
  shipping-cost noise rejected), so forks show their real price and no cheap-looking fork number
  is wrong.
- **Filters** — style, wheel size, fork travel, brand, price range, stock status, and component
  to find the exact product you're looking for.
- **Add to build** — pick your part per component from the cheapest sellers and assemble the
  bike; "My Build" panel keeps a running total, saved to `data/builds.json`.
- **Honesty gate** — every result is a direct product page, NEW, in-stock (or flagged unknown),
  with a working buy link. Wrong-spec (wheel/travel) and used items are rejected.

## How it searches

ShipDeal drives the self-hosted Firecrawl instance (`https://firecrawl.local.zeusserver.io/`)
- `POST /v2/scrape` for retailer and product pages;
- `authoritative_price()` extracts the real listing price (modal price on the product card, with
  shipping-fee / financing noise rejected);
- `link_ok()` confirms the product page actually loads and isn't a homepage redirect;
- `title_relevant()` rejects used/second-hand and wrong-kind items.

Region delivery is a **caveat, not a guarantee**: ShipDeal prefers regional retailers and marks
"shipping unknown" where a retailer doesn't state to-region delivery, so you confirm before
ordering (mirrors the EU/UK anti-dumping caveat for frames).

## Product spec — for interface design (Claude Design)

ShipDeal is a lightweight marketplace for bike builders. The UI must make the **honesty of a
deal** instantly visible: real price, confirmed stock, and a working buy link — never a
misleading cheap number.

**Screens / flows**

1. **Search landing** — a single form: Region (EU/UK, US, AU, Global), Component
   (frame/fork/rear shock/wheelset/tires/drivetrain/brakes/cockpit/pedals/saddle), free-text
   query, Brand (optional), Style (XC/enduro/freeride/downhill/e-bike), Wheel (29/27.5), min
   fork travel, price min/max, and stock (any / in-stock only). One search action.

2. **Results gallery** — one card per genuine product, **cheapest first**. Each card:
   - product picture (og:image)
   - brand + name
   - **exact price** in native currency plus ~GBP conversion
   - **stock status** as a colour badge (green = in stock, amber = unknown, red = out of stock /
     rejected) plus the evidence phrase ("in stock", "add to cart")
   - wheel-size + fork-travel tags (so the exact-spec part is visible)
   - shipping hint for the chosen region
   - a primary **"Buy cheapest →"** button (opens the direct product page)
   - an **"Add to build"** button (adds the pick to the cart)

3. **My Build panel** — persistent side panel listing the chosen part per component with
   picture, price, buy link, and a **running total in GBP**. Remove buttons per item. Balanced
   against the gallery so users assemble their bike as they browse.

**Visual direction**

- Bike-industry marketplace tone: clean, price-first, scannable. Cards lay out picture + price
  + stock badge left-to-right; filters sit in one compact row above the gallery.
- Stock badge must read at a glance (green/amber/red) with a tooltip for the evidence.
- Cheap-noise reassurance: surface the "authoritative price" as the official listing price so
  nobody mistakes a fee/shipping line for the deal.
- Responsive: cards stack vertically on mobile; filters collapse.

**Data wiring (already implemented — reuse as-is)**

- `catalogue.py` COMPONENTS (component budgets, brands, wheel/travel flags, style defaults)
- `filters.py` Filters + apply() (style/wheel/travel/brand/price/stock/component)
- `stock_checker.py` check_stock/passes_stock (fork-strict, evidence string)
- `price.py` nail_price (authoritative modal price)
- `builds.py` Pick/add/total/load/save (data/builds.json) — cart persistence
- `search.py` find_cheapest (multi-retailer Firecrawl search, cheapest-first)
- `app.py` Handler renders HTML; POST `/build/add` + `/build/remove` drive the cart.

## Getting started

```bash
pip install -r requirements.txt
python app.py --port 8018
```

Open http://localhost:8018, choose your region + part, search, and pick your build.

## Repo layout

```
shipdeal/
  README.md
  app.py            — dashboard: search form + filters + gallery + build cart (http.server)
  search.py         — Firecrawl multi-retailer search (cheapest-first, honesty gate)
  catalogue.py      — curated MTB build catalogue (components, budgets, style defaults)
  regions.py        — retailer → region shipping hints + scrapable flags
  stock_checker.py  — stock gate (forks strictly in stock; evidence string)
  price.py          — authoritative (exact) price nailing
  filters.py        — Filters dataclass + apply() predicate
  builds.py         — build cart (Pick/add/total, persists data/builds.json)
  requirements.txt
  tests/            — test_catalogue, test_regions, test_stock, test_price, test_filters,
                      test_builds, test_dashboard (PYTHONPATH=. python3 tests/test_*.py)
```

## Roadmap

- [x] Region shipping verification (per-retailer POSTAGE model + delivery-cost function)
- [x] Brand filter and exact wheel/travel spec enforcement per style
- [x] Delivered cost included in every price and build total
- [x] Saved-build / "My Build" picker panel
- [ ] Continuous/hourly re-scrapes to refresh cheapest prices (cron collector)
