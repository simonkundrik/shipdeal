"""Catalog orchestrator — fan out a full product pull across components x brands x retailers.

Goal: the site's catalogue must not miss anything. For every curated component we pull its
credible brands (COMPONENTS[component]['brands']) across every scrapable retailer, plus the
component-wide search and the retailer collection pages. Rows are deduped by (url, retailer)
in populate.add_row, and delivery-inclusive totals are applied. After the pull we emit a
coverage report: rows per (component, retailer), which retailer x component combos are empty
(gaps), and any component with zero products.
"""
from __future__ import annotations

import json
import sys
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent / "mtb_deals"))
from scraper import fetch_scrape  # noqa: E402
from catalogue import COMPONENTS  # noqa: E402
from regions import RETAILERS, collections_for  # noqa: E402
from populate import (  # noqa: E402
    load_products, save_products, add_row, scrape_item, collect_links,
)

REGION = "Global"  # deliverable-inclusive prices for the ring; country model re-prices per view


def _sources(retailer, component, query, brand):
    """List-URL + collection pages for a retailer/component/brand search."""
    srcs = [RETAILERS[retailer]["list"](query.replace(" ", "+"))]
    if brand:
        srcs += collections_for(retailer, component)
    return srcs


def run_job(component, brand, limit, db, lock):
    """Pull one component x brand across the scrapable ring; merge rows."""
    client = httpx.Client(timeout=75)
    comp = COMPONENTS[component]
    queries = [component] if not brand else [f"{component} {brand}"]
    for retailer in RETAILERS:
        if not RETAILERS[retailer].get("scrapable"):
            continue
        for q in queries:
            for src in _sources(retailer, component, q, brand):
                md = fetch_scrape(src, client)
                if not md:
                    time.sleep(0.5)
                    continue
                links = collect_links(md, retailer)
                for u in links[:limit]:
                    row = scrape_item(u, retailer, REGION, component, brand or retailer,
                                      component, client)
                    if row:
                        with lock:
                            add_row(db, row)
                        time.sleep(0.4)
                time.sleep(0.4)


def tasks():
    """Every (component, brand) job to fan out."""
    out = []
    for comp in COMPONENTS:
        out.append((comp, ""))  # component-wide search
        for b in (COMPONENTS[comp].get("brands") or "").split(","):
            b = b.strip()
            if b:
                out.append((comp, b))
    return out


def coverage(db):
    """Rows by component and by (component, retailer); empty / gapped combos."""
    rows = db["products"]
    by_comp = Counter(r.get("component") for r in rows)
    by_comp_ret = Counter((r.get("component"), r.get("retailer")) for r in rows)
    empty = []
    for comp in COMPONENTS:
        if by_comp[comp] == 0:
            empty.append((comp, "NO PRODUCTS"))
    for comp in COMPONENTS:
        for retailer in RETAILERS:
            if RETAILERS[retailer].get("scrapable") and by_comp_ret[(comp, retailer)] == 0:
                empty.append((comp, retailer))
    return by_comp, by_comp_ret, empty


def main(limit=12, jobs=None):
    db = load_products()
    lock = threading.Lock()
    all_tasks = tasks()
    if jobs:
        all_tasks = jobs

    threads = []
    for comp, brand in all_tasks:
        th = threading.Thread(target=run_job, args=(comp, brand, limit, db, lock))
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    save_products(db)

    by_comp, by_comp_ret, empty = coverage(db)
    print("TOTAL rows:", len(db["products"]))
    print("By component:", dict(by_comp))
    print("Gaps / empty (component, retailer):", empty)
    print("Saved to data/products.json")


if __name__ == "__main__":
    main(limit=int(sys.argv[1]) if len(sys.argv) > 1 else 12)
