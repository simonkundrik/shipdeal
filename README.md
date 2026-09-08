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
  app.py          — region-aware search dashboard (http.server)
  search.py       — Firecrawl search + honesty gate (reused from mtb_deals toolchain)
  regions.py      — retailer → region shipping hints
  requirements.txt
```

## Roadmap

- [ ] Region shipping verification (retailer API / to-region delivery lookup per retailer)
- [ ] Brand filter and exact wheel/travel spec enforcement per style
- [ ] Continuous/hourly re-scrapes to refresh cheapest prices (cron collector)
- [ ] Saved-build / "My Build" picker panel (as in the MTB dashboard)
