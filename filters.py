"""Filters — narrow results to the exact part the user is looking for."""
from dataclasses import dataclass


@dataclass
class Filters:
    style: str = "enduro"
    wheel: str = ""          # "" | "29" | "27.5"
    travel_min: int = 0
    brand: str = ""
    price_min: int = 0
    price_max: int = 99999
    stock: str = ""          # "" | "in_stock"
    component: str = ""      # "" | any COMPONENTS key


def apply(row, f: Filters) -> bool:
    if f.component and row.get("component") != f.component:
        return False
    if f.wheel and row.get("wheel") != f.wheel:
        return False
    if f.brand and f.brand.lower() not in (row.get("brand") or "").lower():
        return False
    gbp = row.get("price_gbp") or 0
    if not (f.price_min <= gbp <= f.price_max):
        return False
    if f.stock == "in_stock" and row.get("stock") != "in_stock":
        return False
    if f.travel_min and (row.get("travel") or 0) < f.travel_min:
        return False
    return True
