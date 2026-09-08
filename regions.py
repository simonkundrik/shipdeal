"""Retailer -> region delivery hints for ShipDeal.

Shipping is a caveat, not a guarantee: we prefer retailers known to deliver to the chosen
region and flag "shipping unknown" where the retailer doesn't state to-region delivery.
Base URLs are used to build collection/search pages; product pages are verified live.
"""
from __future__ import annotations

REGIONS = {
    "EU/UK": ("EU / UK", ["probikesupply", "chainreactioncycles", "huntbikewheels"]),
    "US": ("USA", ["probikesupply", "boxcomponents", "amazon"]),
    "AU": ("Australia", ["probikesupply", "huntbikewheels"]),
    "Global": ("Worldwide", ["probikesupply", "icancycling", "winspace", "yoeleo", "aliexpress"]),
}

# Retailer profile: base domain + how to build a product-list URL + shipping hint.
RETAILERS = {
    "probikesupply": {
        "base": "https://www.probikesupply.com",
        "list": lambda q: f"https://www.probikesupply.com/search?q={q}",
        "ships": {"EU/UK": "likely (shop ships internationally)", "US": "yes", "AU": "yes",
                  "Global": "likely"},
    },
    "chainreactioncycles": {
        "base": "https://www.chainreactioncycles.com",
        "list": lambda q: f"https://www.chainreactioncycles.com/q/{q}",
        "ships": {"EU/UK": "yes", "US": "yes", "AU": "yes", "Global": "likely"},
    },
    "huntbikewheels": {
        "base": "https://www.huntbikewheels.com",
        "list": lambda q: f"https://www.huntbikewheels.com/search?q={q}",
        "ships": {"EU/UK": "yes", "US": "likely", "AU": "yes", "Global": "likely"},
    },
    "boxcomponents": {
        "base": "https://www.boxcomponents.com",
        "list": lambda q: f"https://www.boxcomponents.com/search?q={q}",
        "ships": {"EU/UK": "likely", "US": "yes", "AU": "likely", "Global": "likely"},
    },
    "amazon": {
        "base": "https://www.amazon.com",
        "list": lambda q: f"https://www.amazon.com/s?k={q}",
        "ships": {"EU/UK": "many ship to UK", "US": "yes", "AU": "likely", "Global": "varies"},
    },
    "icancycling": {
        "base": "https://www.icancycling.com",
        "list": lambda q: f"https://www.icancycling.com/search?q={q}",
        "ships": {"EU/UK": "likely", "US": "likely", "AU": "likely", "Global": "yes"},
    },
    "winspace": {
        "base": "https://winspace.cc",
        "list": lambda q: f"https://winspace.cc/search?q={q}",
        "ships": {"Global": "yes (factory-direct)"},
    },
    "yoeleo": {
        "base": "https://www.yoeleo.com",
        "list": lambda q: f"https://www.yoeleo.com/search?q={q}",
        "ships": {"Global": "yes (factory-direct)"},
    },
    "aliexpress": {
        "base": "https://www.aliexpress.com",
        "list": lambda q: f"https://www.aliexpress.com/w/wholesale-{q.replace(' ', '-')}.html",
        "ships": {"Global": "yes", "EU/UK": "yes", "US": "yes", "AU": "yes"},
    },
}


def retailers_for(region):
    return REGIONS.get(region, REGIONS["Global"])[1]


def shipping_hint(retailer, region):
    return RETAILERS[retailer]["ships"].get(region, "shipping unknown")
