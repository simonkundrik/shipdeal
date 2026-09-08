"""Stock checker — critical.

Forks must be confirmed IN STOCK (a decisive "in stock"/"add to cart" signal); anything else
is rejected. Other components reject only a confirmed out-of-stock, so "unknown" is acceptable
(loosened for niche brands). Decisive in-stock phrases override Amazon "currently unavailable"
boilerplate.
"""
STRONG_IN = ["in stock", "add to cart", "ready to ship", "left in stock", "in-stock", "ships"]
STRONG_OUT = ["out of stock", "sold out", "no longer available", "back order", "discontinued"]


def check_stock(md, component):
    """Return (status, evidence). status in {in_stock, out_of_stock, unknown}."""
    low = (md or "").lower()
    hits_in = [s for s in STRONG_IN if s in low]
    hits_out = [s for s in STRONG_OUT if s in low]
    if hits_in and not hits_out:
        status, evidence = "in_stock", max(hits_in, key=len)
    elif hits_out:
        status, evidence = "out_of_stock", max(hits_out, key=len)
    else:
        status, evidence = "unknown", "no stock signal"
    if component == "fork" and status != "in_stock":
        evidence += " [FORKS MUST BE IN STOCK]"
    return status, evidence


def passes_stock(status, component):
    """Stock gate per component. Forks strictly in_stock; others reject only out_of_stock."""
    if component == "fork":
        return status == "in_stock"
    return status != "out_of_stock"
