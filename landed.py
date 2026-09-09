"""Landed-cost model — the true delivered price a shopper pays.

A listed price is converted to the destination currency (FX), shipping added, then an import
duty is applied when the goods value crosses the de-minimis threshold, VAT applied (EU OSS net
scheme), and a customs clearance fee added when the parcel crosses a customs border. Sorting the
comparison on landed cost (not list price) is what makes ShipDeal a true cross-country comparison.
"""


def landed_cost(list_price, currency="GBP", fx=1.0, ship=0.0, duty_rate=0.0,
                vat_rate=0.0, de_minimis=135.0, clearance=0.0):
    """Landed GBP = (goods*FX + ship) + duty(if goods>de_minimis) + VAT + clearance."""
    goods_gbp = float(list_price) * fx
    base = goods_gbp + ship
    crosses = goods_gbp > de_minimis
    duty = goods_gbp * duty_rate if crosses else 0.0
    taxable = base + duty
    vat = taxable * vat_rate
    clearance_fee = clearance if crosses else 0.0
    return round(base + duty + vat + clearance_fee, 2)


def landed_row(row, info):
    """True delivered price for a DB row (price_gbp + shipping) under a country's tax/duty."""
    goods = row.get("price_gbp") or 0.0
    ship = row.get("shipping_gbp")
    ship = ship if ship is not None else 0.0
    return landed_cost(goods, "GBP", 1.0, ship,
                       info.get("duty_rate", 0), info.get("vat_rate", 0),
                       info.get("de_minimis", 135), info.get("clearance_fee", 0))
