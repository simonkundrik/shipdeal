"""Retailer origin + per-zone postage. Merge into regions.py (keep REGIONS/RETAILERS/COLLECTIONS).

A retailer missing a zone DOES NOT DELIVER there: drop the row and count it, never price it at 0.
Zones: UK, EU, EUX (Switzerland/Norway), NA (US/Canada), OC (Australia/New Zealand).
"""
from __future__ import annotations

ORIGIN = {
    "probikesupply":       {"country": "NL", "customs": "EU", "vat_rate": 0.21},
    "chainreactioncycles": {"country": "IE", "customs": "EU", "vat_rate": 0.23},
    "huntbikewheels":      {"country": "GB", "customs": "UK", "vat_rate": 0.20},
    "boxcomponents":       {"country": "US", "customs": "US", "vat_rate": 0.0},
    "amazon":              {"country": "US", "customs": "US", "vat_rate": 0.0},
    "icancycling":         {"country": "CN", "customs": "CN", "vat_rate": 0.0},
    "winspace":            {"country": "CN", "customs": "CN", "vat_rate": 0.0},
    "yoeleo":              {"country": "CN", "customs": "CN", "vat_rate": 0.0},
    "aliexpress":          {"country": "CN", "customs": "CN", "vat_rate": 0.0},
}

# cost_gbp, free_over_gbp (None = never free), days
ZONE_POSTAGE = {
    "probikesupply": {
        "UK":  {"cost_gbp": 14.0, "free_over_gbp": None, "days": 4},
        "EU":  {"cost_gbp": 9.0,  "free_over_gbp": 180,  "days": 3},
        "EUX": {"cost_gbp": 19.0, "free_over_gbp": None, "days": 5},
        "NA":  {"cost_gbp": 26.0, "free_over_gbp": None, "days": 8},
        "OC":  {"cost_gbp": 34.0, "free_over_gbp": None, "days": 12},
    },
    "chainreactioncycles": {
        "UK":  {"cost_gbp": 6.0,  "free_over_gbp": 100,  "days": 3},
        "EU":  {"cost_gbp": 8.0,  "free_over_gbp": 150,  "days": 4},
        "EUX": {"cost_gbp": 18.0, "free_over_gbp": None, "days": 6},
        "NA":  {"cost_gbp": 22.0, "free_over_gbp": None, "days": 8},
        "OC":  {"cost_gbp": 28.0, "free_over_gbp": None, "days": 11},
    },
    "huntbikewheels": {
        "UK":  {"cost_gbp": 0.0,  "free_over_gbp": 0,    "days": 2},
        "EU":  {"cost_gbp": 19.0, "free_over_gbp": None, "days": 5},
        "EUX": {"cost_gbp": 24.0, "free_over_gbp": None, "days": 7},
        "NA":  {"cost_gbp": 29.0, "free_over_gbp": None, "days": 8},
        "OC":  {"cost_gbp": 39.0, "free_over_gbp": None, "days": 12},
    },
    "boxcomponents": {
        "NA":  {"cost_gbp": 9.0,  "free_over_gbp": None, "days": 4},
        "UK":  {"cost_gbp": 28.0, "free_over_gbp": None, "days": 9},
        "EU":  {"cost_gbp": 30.0, "free_over_gbp": None, "days": 9},
        "EUX": {"cost_gbp": 34.0, "free_over_gbp": None, "days": 11},
        "OC":  {"cost_gbp": 38.0, "free_over_gbp": None, "days": 12},
    },
    "amazon": {
        "NA":  {"cost_gbp": 0.0,  "free_over_gbp": 0,    "days": 3},
        "UK":  {"cost_gbp": 16.0, "free_over_gbp": None, "days": 8},
        "EU":  {"cost_gbp": 18.0, "free_over_gbp": None, "days": 8},
        "EUX": {"cost_gbp": 22.0, "free_over_gbp": None, "days": 10},
        "OC":  {"cost_gbp": 26.0, "free_over_gbp": None, "days": 12},
    },
    "winspace": {
        "UK":  {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 9},
        "EU":  {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 9},
        "EUX": {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 11},
        "NA":  {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 8},
        "OC":  {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 10},
    },
    "icancycling": {
        "UK":  {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 11},
        "EU":  {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 11},
        "EUX": {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 13},
        "NA":  {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 10},
        "OC":  {"cost_gbp": 0.0, "free_over_gbp": 0, "days": 12},
    },
}


def origin_of(retailer):
    return ORIGIN.get(retailer, {"country": "??", "customs": "??", "vat_rate": 0.0})


def postage(retailer, zone, price_gbp):
    """(cost_gbp, days) or (None, None) when this retailer does not deliver to the zone."""
    entry = ZONE_POSTAGE.get(retailer, {}).get(zone)
    if not entry:
        return None, None
    cost = entry["cost_gbp"]
    free_over = entry["free_over_gbp"]
    if free_over is not None and price_gbp >= free_over:
        cost = 0.0
    return cost, entry["days"]
