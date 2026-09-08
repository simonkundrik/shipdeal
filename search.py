"""ShipDeal search engine — cheapest NEW part that delivers to your region.

Drives the self-hosted Firecrawl instance (https://firecrawl.local.zeusserver.io/), filters to
genuine NEW in-stock product pages with working direct buy links, rejects used/second-hand and
shipping-fee/financing noise prices, and returns options sorted cheapest with picture + link.
"""
from __future__ import annotations
import re
import sys
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent / "mtb_deals"))
from scraper import (  # noqa: E402
    detect_stock, fetch_scrape, get_image, link_ok, title_relevant, authoritative_price,
)
from regions import retailers_for, shipping_hint  # noqa: E402


def _scan(retailer, query, client):
    try:
        from regions import RETAILERS
        url = RETAILERS[retailer]["list"](query.replace(" ", "+"))
    except Exception:  # noqa: BLE001
        return [], None
    md = fetch_scrape(url, client)
    if not md:
        return [], None
    links = [m.group(2) for m in re.finditer(r"\[([^\]]+)\]\(([^)\s]+)\)", md)
             if "/products/" in m.group(2) and "/cdn/" not in m.group(2)]
    return sorted(set(links)), url


def find_cheapest(query, region, brand="", budget_gbp=600, limit=6):
    """Return NEW in-stock genuine product pages, sorted cheapest, for a query + region."""
    client = httpx.Client(timeout=75)
    part = {"id": "part", "name": query, "budget_gbp": budget_gbp,
            "min_price": 8, "max_price": budget_gbp}
    results = []
    seen = set()
    for retailer in retailers_for(region):
        ships = shipping_hint(retailer, region)
        links, _list_url = _scan(retailer, query, client)
        for u in links:
            if u in seen:
                continue
            seen.add(u)
            pmd = fetch_scrape(u, client)
            if not pmd:
                continue
            stock = detect_stock(pmd)
            if stock == "out_of_stock":
                continue
            d = {"url": u, "title": query, "brand": brand or retailer,
                 "note": "", "src_kind": "product", "src": retailer, "ships": ships}
            if not title_relevant(d, "part"):
                continue
            if any(w in u.lower() for w in ("used", "buycycle", "for-sale", "refurbished",
                                            "pre-owned", "second-hand")):
                continue
            # authoritative listing price within budget (rejects fee/financing noise)
            authoritative_price(d, part, client)
            if not d.get("price_gbp"):
                continue
            d["image"] = get_image(u, client)
            d["link_ok"] = link_ok(u, client)
            if not d["link_ok"]:
                continue
            results.append(d)
            time.sleep(0.4)
        if len(results) >= limit:
            break
    results.sort(key=lambda d: d.get("price_gbp") or 1e9)
    return results[:limit]


def run(query, region="EU/UK", brand="", budget_gbp=600, limit=6):
    opts = find_cheapest(query, region, brand, budget_gbp, limit)
    return [{
        "brand": o.get("brand"), "price": o.get("price"), "currency": o.get("currency"),
        "price_gbp": o.get("price_gbp"), "image": o.get("image"), "url": o.get("url"),
        "stock": o.get("in_stock", "unknown"), "ships": o.get("ships", "shipping unknown"),
    } for o in opts]
