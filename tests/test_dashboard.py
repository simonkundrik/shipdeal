"""RED: dashboard exposes parse_filters and renders filter form + build-cart UI."""
from app import parse_filters, render

f = parse_filters({"style": "enduro", "wheel": "29", "travel": "170", "brand": "Marzocchi",
                   "min": "100", "max": "500", "stock": "in_stock", "component": "fork"})
assert f.style == "enduro" and f.wheel == "29"
assert f.travel_min == 170 and f.brand == "Marzocchi"
assert f.price_min == 100 and f.price_max == 500
assert f.stock == "in_stock" and f.component == "fork"

page = render(region="EU/UK", query="fork", brand="Marzocchi", budget=600, results=[],
              message="", filters=f)
assert "Add to build" in page
assert "My Build" in page
assert "Choose" in page
assert "Buy cheapest" in page
# Trailhead design tokens are applied to the rendered page
assert "#F2EDE3" in page and "#B94A26" in page and "#16211C" in page
assert "Big+Shoulders" in page and "DM+Mono" in page
print("dashboard tests OK")
