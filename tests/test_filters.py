"""RED: Filters must apply component/wheel/brand/price/stock/travel predicates."""
from filters import Filters, apply

r = {"component": "fork", "wheel": "29", "brand": "Marzocchi",
     "price_gbp": 425.1, "stock": "in_stock", "travel": 180}
assert apply(r, Filters(style="enduro", wheel="29", travel_min=170, stock="in_stock")) is True
assert apply(r, Filters(wheel="27.5")) is False
assert apply(r, Filters(brand="Fox")) is False
assert apply(r, Filters(price_min=500)) is False
assert apply(r, Filters(price_max=400)) is False
assert apply(r, Filters(component="brakes")) is False
assert apply(r, Filters(stock="in_stock")) is True
assert apply(r, Filters(stock="")) is True
assert apply(r, Filters(travel_min=200)) is False
print("filters OK")
