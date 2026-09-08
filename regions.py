"""Retailer -> region delivery hints for ShipDeal.

Shipping is a caveat, not a guarantee: we prefer retailers known to deliver to the chosen
region and flag "shipping unknown" where the retailer doesn't state to-region delivery.
Base URLs are used to build collection/search pages; product pages are verified live.
scrapable=False marks bot-walled stores that Firecrawl cannot list (skip them in the ring).
"""
from __future__ import annotations

REGIONS = {
    "EU/UK": ("EU / UK", ["probikesupply", "chainreactioncycles", "huntbikewheels"]),
    "US": ("USA", ["probikesupply", "boxcomponents", "amazon"]),
    "AU": ("Australia", ["probikesupply", "huntbikewheels"]),
    "Global": ("Worldwide", ["probikesupply", "icancycling", "winspace", "yoeleo", "aliexpress"]),
}

# Retailer profile: base domain + list-URL builder + shipping hint + scrapable flag.
RETAILERS = {
    "probikesupply": {
        "base": "https://www.probikesupply.com",
        "list": lambda q: f"https://www.probikesupply.com/search?q={q}",
        "scrapable": True,
        "ships": {"EU/UK": "likely (shop ships internationally)", "US": "yes", "AU": "yes",
                  "Global": "likely"},
    },
    "chainreactioncycles": {
        "base": "https://www.chainreactioncycles.com",
        "list": lambda q: f"https://www.chainreactioncycles.com/q/{q}",
        "scrapable": True,
        "ships": {"EU/UK": "yes", "US": "yes", "AU": "yes", "Global": "likely"},
    },
    "huntbikewheels": {
        "base": "https://www.huntbikewheels.com",
        "list": lambda q: f"https://www.huntbikewheels.com/search?q={q}",
        "scrapable": True,
        "ships": {"EU/UK": "yes", "US": "likely", "AU": "yes", "Global": "likely"},
    },
    "boxcomponents": {
        "base": "https://www.boxcomponents.com",
        "list": lambda q: f"https://www.boxcomponents.com/search?q={q}",
        "scrapable": True,
        "ships": {"EU/UK": "likely", "US": "yes", "AU": "likely", "Global": "likely"},
    },
    "amazon": {
        "base": "https://www.amazon.com",
        "list": lambda q: f"https://www.amazon.com/s?k={q}",
        "scrapable": True,
        "ships": {"EU/UK": "many ship to UK", "US": "yes", "AU": "likely", "Global": "varies"},
    },
    "icancycling": {
        "base": "https://www.icancycling.com",
        "list": lambda q: f"https://www.icancycling.com/search?q={q}",
        "scrapable": True,
        "ships": {"EU/UK": "likely", "US": "likely", "AU": "likely", "Global": "yes"},
    },
    "winspace": {
        "base": "https://winspace.cc",
        "list": lambda q: f"https://winspace.cc/search?q={q}",
        "scrapable": True,
        "ships": {"Global": "yes (factory-direct)"},
    },
    "yoeleo": {
        "base": "https://www.yoeleo.com",
        "list": lambda q: f"https://www.yoeleo.com/search?q={q}",
        "scrapable": True,
        "ships": {"Global": "yes (factory-direct)"},
    },
    "aliexpress": {
        "base": "https://www.aliexpress.com",
        "list": lambda q: f"https://www.aliexpress.com/w/wholesale-{q.replace(' ', '-')}.html",
        "scrapable": True,
        "ships": {"Global": "yes", "EU/UK": "yes", "US": "yes", "AU": "yes"},
    },
}


def retailers_for(region):
    return REGIONS.get(region, REGIONS["Global"])[1]


def shipping_hint(retailer, region):
    return RETAILERS[retailer]["ships"].get(region, "shipping unknown")


# Delivery cost per retailer-region, in GBP. free_over_gbp: at/above this price delivery is free.
# cost_gbp None = delivery unknown (flagged in the UI, never silently assumed zero).
POSTAGE = {
    "probikesupply": {"EU/UK": {"cost_gbp": 25.0, "free_over_gbp": None},
                      "US": {"cost_gbp": 0.0, "free_over_gbp": 0},
                      "AU": {"cost_gbp": 30.0, "free_over_gbp": None},
                      "Global": {"cost_gbp": 35.0, "free_over_gbp": 400}},
    "chainreactioncycles": {"EU/UK": {"cost_gbp": 0.0, "free_over_gbp": 0},
                            "US": {"cost_gbp": 12.0, "free_over_gbp": 0},
                            "AU": {"cost_gbp": 15.0, "free_over_gbp": 0},
                            "Global": {"cost_gbp": 20.0, "free_over_gbp": None}},
    "huntbikewheels": {"EU/UK": {"cost_gbp": 0.0, "free_over_gbp": 30},
                       "US": {"cost_gbp": 12.0, "free_over_gbp": 100},
                       "AU": {"cost_gbp": 15.0, "free_over_gbp": 100},
                       "Global": {"cost_gbp": 20.0, "free_over_gbp": 150}},
    "boxcomponents": {"US": {"cost_gbp": 0.0, "free_over_gbp": 0},
                      "EU/UK": {"cost_gbp": 20.0, "free_over_gbp": 150},
                      "Global": {"cost_gbp": 20.0, "free_over_gbp": 150}},
    "amazon": {"US": {"cost_gbp": 0.0, "free_over_gbp": 35},
               "EU/UK": {"cost_gbp": 5.0, "free_over_gbp": None},
               "Global": {"cost_gbp": 8.0, "free_over_gbp": None}},
    "icancycling": {"Global": {"cost_gbp": 30.0, "free_over_gbp": 400},
                    "EU/UK": {"cost_gbp": 30.0, "free_over_gbp": 400},
                    "US": {"cost_gbp": 30.0, "free_over_gbp": 400},
                    "AU": {"cost_gbp": 35.0, "free_over_gbp": 400}},
    "winspace": {"Global": {"cost_gbp": 40.0, "free_over_gbp": 400},
                 "EU/UK": {"cost_gbp": 40.0, "free_over_gbp": 400},
                 "US": {"cost_gbp": 40.0, "free_over_gbp": 400},
                 "AU": {"cost_gbp": 45.0, "free_over_gbp": 400}},
    "yoeleo": {"Global": {"cost_gbp": 30.0, "free_over_gbp": 350},
               "EU/UK": {"cost_gbp": 30.0, "free_over_gbp": 350},
               "US": {"cost_gbp": 30.0, "free_over_gbp": 350},
               "AU": {"cost_gbp": 35.0, "free_over_gbp": 350}},
    "aliexpress": {"Global": {"cost_gbp": 0.0, "free_over_gbp": 0},
                   "EU/UK": {"cost_gbp": 0.0, "free_over_gbp": 0},
                   "US": {"cost_gbp": 0.0, "free_over_gbp": 0},
                   "AU": {"cost_gbp": 0.0, "free_over_gbp": 0}},
}


def delivery_cost_gbp(retailer, region, price_gbp):
    """Delivery cost to add to the price. cost None = unknown; free_over makes delivery free."""
    entry = POSTAGE.get(retailer, {}).get(region)
    if not entry:
        return None, None
    free_over = entry["free_over_gbp"]
    cost = entry["cost_gbp"]
    if free_over is not None and price_gbp >= free_over:
        cost = 0.0
    return cost, free_over
