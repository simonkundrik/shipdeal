"""Per-country landed-cost parameters (17 countries) - the table the Trailhead design assumes.

All money arithmetic happens in GBP (rows already carry price_gbp from price.py).
gbp_to_local is DISPLAY ONLY: multiply a GBP amount by it to render the local price.
duty_free_gbp / tax_free_gbp are de-minimis thresholds on goods value + shipping, in GBP.
customs groups countries that trade without a border between them; zone selects postage.
"""
from __future__ import annotations

_EU = dict(customs="EU", zone="EU", duty_rate=0.047, clearance_fee_gbp=15,
           duty_free_gbp=129, tax_free_gbp=0, currency="EUR", symbol="\u20ac",
           symbol_after=False, decimals=2, gbp_to_local=1.16, group="Europe")


def _eu(name, vat, **over):
    return {**_EU, "name": name, "vat_rate": vat, **over}


COUNTRY_INFO = {
    "GB": {"name": "United Kingdom", "group": "Europe", "currency": "GBP", "symbol": "\u00a3",
           "symbol_after": False, "decimals": 2, "gbp_to_local": 1.0, "vat_rate": 0.20,
           "duty_rate": 0.041, "customs": "UK", "zone": "UK", "clearance_fee_gbp": 12,
           "duty_free_gbp": 135, "tax_free_gbp": 0},
    "IE": _eu("Ireland", 0.23),
    "DE": _eu("Germany", 0.19),
    "FR": _eu("France", 0.20),
    "NL": _eu("Netherlands", 0.21),
    "AT": _eu("Austria", 0.20),
    "ES": _eu("Spain", 0.21),
    "IT": _eu("Italy", 0.22),
    "PL": _eu("Poland", 0.23, currency="PLN", symbol=" z\u0142", symbol_after=True,
              decimals=0, gbp_to_local=5.05, clearance_fee_gbp=13),
    "SE": _eu("Sweden", 0.25, currency="SEK", symbol=" kr", symbol_after=True,
              decimals=0, gbp_to_local=13.4, clearance_fee_gbp=14),
    "DK": _eu("Denmark", 0.25, currency="DKK", symbol=" kr", symbol_after=True,
              decimals=0, gbp_to_local=8.65, clearance_fee_gbp=14),
    "CH": {"name": "Switzerland", "group": "Europe", "currency": "CHF", "symbol": "CHF ",
           "symbol_after": False, "decimals": 2, "gbp_to_local": 1.12, "vat_rate": 0.081,
           "duty_rate": 0.02, "customs": "CH", "zone": "EUX", "clearance_fee_gbp": 16,
           "duty_free_gbp": 0, "tax_free_gbp": 0},
    "NO": {"name": "Norway", "group": "Europe", "currency": "NOK", "symbol": " kr",
           "symbol_after": True, "decimals": 0, "gbp_to_local": 13.6, "vat_rate": 0.25,
           "duty_rate": 0.025, "customs": "NO", "zone": "EUX", "clearance_fee_gbp": 14,
           "duty_free_gbp": 0, "tax_free_gbp": 0},
    "US": {"name": "United States", "group": "North America", "currency": "USD", "symbol": "$",
           "symbol_after": False, "decimals": 2, "gbp_to_local": 1.27, "vat_rate": 0.072,
           "duty_rate": 0.0, "customs": "US", "zone": "NA", "clearance_fee_gbp": 0,
           "duty_free_gbp": 630, "tax_free_gbp": 630},
    "CA": {"name": "Canada", "group": "North America", "currency": "CAD", "symbol": "C$",
           "symbol_after": False, "decimals": 2, "gbp_to_local": 1.73, "vat_rate": 0.13,
           "duty_rate": 0.05, "customs": "CA", "zone": "NA", "clearance_fee_gbp": 10,
           "duty_free_gbp": 16, "tax_free_gbp": 16},
    "AU": {"name": "Australia", "group": "Oceania", "currency": "AUD", "symbol": "A$",
           "symbol_after": False, "decimals": 2, "gbp_to_local": 1.93, "vat_rate": 0.10,
           "duty_rate": 0.05, "customs": "AU", "zone": "OC", "clearance_fee_gbp": 0,
           "duty_free_gbp": 518, "tax_free_gbp": 0},
    "NZ": {"name": "New Zealand", "group": "Oceania", "currency": "NZD", "symbol": "NZ$",
           "symbol_after": False, "decimals": 2, "gbp_to_local": 2.10, "vat_rate": 0.15,
           "duty_rate": 0.05, "customs": "NZ", "zone": "OC", "clearance_fee_gbp": 0,
           "duty_free_gbp": 0, "tax_free_gbp": 0},
}

DEFAULT_COUNTRY = "GB"
# Legacy region buckets -> a representative country, so old links keep working.
REGION_ALIAS = {"EU/UK": "GB", "US": "US", "AU": "AU", "Global": "GB"}


def country_info(cc):
    return COUNTRY_INFO.get(cc, COUNTRY_INFO[DEFAULT_COUNTRY])


def zone_of(cc):
    return country_info(cc)["zone"]


def groups():
    """Ordered [(group, [(cc, name), ...])] for the country <select>'s optgroups."""
    out = []
    for cc, c in COUNTRY_INFO.items():
        for g in out:
            if g[0] == c["group"]:
                g[1].append((cc, c["name"]))
                break
        else:
            out.append((c["group"], [(cc, c["name"])]))
    return out


def money(cc, gbp):
    """Format a GBP amount in the destination country's currency."""
    c = country_info(cc)
    v = float(gbp) * c["gbp_to_local"]
    n = f"{v:,.{c['decimals']}f}"
    return n + c["symbol"] if c["symbol_after"] else c["symbol"] + n


def tax_line(cc):
    """Header caption: '20% VAT - prices in GBP - duty-free under GBP135.00'."""
    c = country_info(cc)
    tax = "sales tax" if cc == "US" else "VAT"
    rate = f"{round(c['vat_rate'] * 1000) / 10:g}% {tax}"
    if c["duty_free_gbp"]:
        duty = "duty-free under " + money(cc, c["duty_free_gbp"])
    else:
        duty = "duty from the first " + c["currency"]
    return f"{rate} \u00b7 prices in {c['currency']} \u00b7 {duty}"
