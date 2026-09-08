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
- **Honesty gate** — every result is a direct product page, NEW, in-stock (or "stock unknown"
  flagged), with a working buy link. Wrong-spec (wheel/travel) and used items are rejected.
- **Cheapest-first** — results sorted by price with the authoritative listing price (fee /
  financing / shipping-cost numbers are never mistaken for the product price).
- **Picture + direct link** — each option shows the product image and a real product-page URL.
- **Selection, not verdict** — multiple genuine options per part so you assemble your own build.

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
