"""Landed cost, origin-aware - replaces landed.py's region-blind model.

A listed price is VAT-inclusive in the RETAILER's home market. What a shopper in country X pays
is not that number:

    net       = list_gbp                      if the sale is domestic
              = list_gbp / (1 + origin_vat)   otherwise (exports are zero-rated)
    ship      = zone postage, free above the retailer's threshold
    duty      = net * duty_rate               when customs areas differ AND net+ship > de-minimis
    vat       = (net+ship+duty) * vat_rate    destination rate (EU OSS / import VAT)
    clearance = clearance_fee                 when duty applies
    landed    = net + ship + duty + vat + clearance

domestic  = retailer customs area == destination customs area, and that area is not "EU".
Intra-EU is deliberately NOT domestic: origin VAT comes off, destination VAT goes on. That is why
the same listing is one price in Germany (19%) and another in Sweden (25%).
"""
from __future__ import annotations

from countries import country_info, money
from shipping import origin_of, postage


def landed(list_gbp, retailer, country):
    c = country_info(country)
    o = origin_of(retailer)
    goods = float(list_gbp or 0.0)

    ship, days = postage(retailer, c["zone"], goods)
    if ship is None:
        return {"serves": False, "total_gbp": None, "label": None, "days": None,
                "origin": o["country"], "crossing": None, "dutiable": False,
                "net": None, "ship": None, "duty": 0.0, "vat": 0.0, "clearance": 0.0,
                "breakdown": f"{retailer} does not deliver to {c['name']}",
                "duty_note": "no delivery"}

    domestic = o["customs"] == c["customs"] and o["customs"] != "EU"
    crossing = o["customs"] != c["customs"]
    net = goods if domestic or not o["vat_rate"] else goods / (1 + o["vat_rate"])

    dutiable = crossing and (net + ship) > c["duty_free_gbp"]
    taxable = False if domestic else (not crossing or (net + ship) > c["tax_free_gbp"])

    duty = net * c["duty_rate"] if dutiable else 0.0
    vat = (net + ship + duty) * c["vat_rate"] if taxable else 0.0
    clearance = float(c["clearance_fee_gbp"]) if dutiable else 0.0
    total = net + ship + duty + vat + clearance

    parts = [("item " if domestic else "net ") + money(country, net),
             "free shipping" if ship == 0 else "ship " + money(country, ship)]
    if duty:
        parts.append(f"{round(c['duty_rate'] * 1000) / 10:g}% duty " + money(country, duty))
    if vat:
        label = "sales tax " if country == "US" else "VAT "
        parts.append(f"{round(c['vat_rate'] * 1000) / 10:g}% " + label + money(country, vat))
    if clearance:
        parts.append("clearance " + money(country, clearance))

    if not crossing:
        note = "no border to cross"
    elif dutiable:
        note = f"import duty + {round(c['vat_rate'] * 100)}% VAT applied"
    elif c["duty_free_gbp"]:
        note = "under the " + money(country, c["duty_free_gbp"]) + " duty threshold"
    else:
        note = "no duty on this line"

    return {"serves": True, "total_gbp": round(total, 2), "label": money(country, total),
            "net": round(net, 2), "ship": round(ship, 2), "duty": round(duty, 2),
            "vat": round(vat, 2), "clearance": round(clearance, 2), "crossing": crossing,
            "dutiable": dutiable, "days": days, "origin": o["country"],
            "duty_note": note, "breakdown": " + ".join(parts)}


def landed_row(row, country):
    """Landed cost for a DB row (price_gbp + its retailer) delivered to `country`."""
    return landed(row.get("price_gbp") or 0.0, row.get("retailer") or "", country)


def sort_by_landed(rows, country):
    """Deliverable rows cheapest-first on landed cost, plus the count that was dropped."""
    priced, hidden = [], 0
    for r in rows:
        L = landed_row(r, country)
        if not L["serves"]:
            hidden += 1
            continue
        priced.append(dict(r, landed=L))
    priced.sort(key=lambda r: r["landed"]["total_gbp"])
    return priced, hidden
