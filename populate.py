"""Populate the ShipDeal product database (data/products.json) across the retailer ring.

Every product row carries the authoritative price PLUS delivery cost (total_gbp), so the
"cheapest retailer" ranking always includes shipping. Dedupe by (url, retailer).
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent / "mtb_deals"))
from scraper import (  # noqa: E402
    fetch_scrape, get_image, link_ok, parse_travel, title_relevant, wheel_match,
)
from catalogue import COMPONENTS  # noqa: E402
from regions import RETAILERS, delivery_cost_gbp, shipping_hint  # noqa: E402
from stock_checker import check_stock, passes_stock  # noqa: E402
from price import nail_price  # noqa: E402

PRODUCTS_FILE = Path(__file__).parent / "data" / "products.json"


def total_with_delivery(price_gbp, delivery_gbp):
    """Total price including delivery. delivery None => total unknown (flagged)."""
    if price_gbp is None:
        return None
    if delivery_gbp is None:
        return None
    return round(price_gbp + delivery_gbp, 2)


def load_products():
    return json.loads(PRODUCTS_FILE.read_text()) if PRODUCTS_FILE.exists() else \
        {"products": [], "scraped_at": None}


def save_products(db):
    PRODUCTS_FILE.parent.mkdir(exist_ok=True)
    PRODUCTS_FILE.write_text(json.dumps(db, indent=2))


def add_row(db, row):
    rows = db["products"]
    key = (row.get("url"), row.get("retailer"))
    if any((r.get("url"), r.get("retailer")) == key for r in rows):
        return db
    rows.append(row)
    return db


def scrape_item(url, retailer, region, component, brand, name, client):
    """Nail one product row: exact price + delivery -> total, stock, wheel/travel, image."""
    pmd = fetch_scrape(url, client)
    if not pmd:
        return None
    stock, ev = check_stock(pmd, component)
    if stock == "out_of_stock":
        return None
    d = {"url": url, "title": name or brand, "brand": brand, "note": "",
         "component": component, "src_kind": "product", "retailer": retailer}
    if not title_relevant(d, component):
        return None
    part = {"id": component, "name": component, "budget_gbp": COMPONENTS[component]["budget"],
            "min_price": COMPONENTS[component]["min"], "max_price": COMPONENTS[component]["max"]}
    ok = nail_price(d, part, client)
    if not ok:
        return None
    price_gbp = d["price_gbp"]
    cost, _free = delivery_cost_gbp(retailer, region, price_gbp)
    shipping_gbp = cost if cost is not None else None
    total_gbp = total_with_delivery(price_gbp, shipping_gbp)
    row = {"component": component, "brand": brand, "name": name or d["title"], "url": url,
           "retailer": retailer, "price": d["price"], "currency": d["currency"],
           "price_gbp": price_gbp, "shipping_gbp": shipping_gbp, "total_gbp": total_gbp,
           "ships_to": region, "ships_hint": shipping_hint(retailer, region),
           "stock": stock, "stock_evidence": ev, "image": get_image(url, client),
           "link_ok": link_ok(url, client),
           "scraped_at": datetime.now(timezone.utc).isoformat()}
    if COMPONENTS[component].get("wheel"):
        row["wheel"] = wheel_match(pmd, d.get("title"), "29")
        row["wheel_explicit"] = None
    if COMPONENTS[component].get("travel"):
        row["travel"] = parse_travel(pmd, d.get("title"))
    return row


def populate(component, region="EU/UK", brand="", limit=6, client=None):
    """Scrape the retailer ring for a component, add rows with delivery-inclusive totals."""
    client = client or httpx.Client(timeout=75)
    db = load_products()
    comp = COMPONENTS[component]
    queries = [component] if not brand else [f"{component} {brand}"]
    for retailer in RETAILERS:
        if not RETAILERS[retailer].get("scrapable"):
            continue
        for q in queries:
            _scan = RETAILERS[retailer]["list"](q.replace(" ", "+"))
            md = fetch_scrape(_scan, client)
            if not md:
                time.sleep(0.5)
                continue
            links = []
            import re
            for m in re.finditer(r"\[([^\]]+)\]\(([^)\s]+)\)", md):
                if "/products/" in m.group(2) and "/cdn/" not in m.group(2) and \
                        m.group(2) not in links:
                    links.append(m.group(2))
            for u in links[:limit]:
                row = scrape_item(u, retailer, region, component, brand or retailer,
                                  component, client)
                if row:
                    add_row(db, row)
                time.sleep(0.4)
    save_products(db)
    n = len(db["products"])
    print(f"populated {component}: {n} rows in {PRODUCTS_FILE}")
    return db


def cheapest_by_component(component, region="EU/UK"):
    """Rows for a component sorted by total incl delivery (delivery-unknown rows last)."""
    db = load_products()
    rows = [r for r in db["products"] if r.get("component") == component]
    rows.sort(key=lambda r: (r.get("total_gbp") if r.get("total_gbp") is not None else 1e9))
    return rows
