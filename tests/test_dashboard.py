"""RED: dashboard exposes parse_filters and renders filter form + build-cart UI."""
from app import parse_filters, render

f = parse_filters({"style": "enduro", "wheel": "29", "travel": "170", "brand": "Marzocchi",
                   "min": "100", "max": "500", "stock": "in_stock", "component": "fork"})
assert f.style == "enduro" and f.wheel == "29"
assert f.travel_min == 170 and f.brand == "Marzocchi"
assert f.price_min == 100 and f.price_max == 500
assert f.stock == "in_stock" and f.component == "fork"

page = render(country="GB", query="fork", brand="Marzocchi", budget=600, results=[],
              message="", filters=f)
assert "Add to build" in page
assert "My Build" in page
assert "Choose" in page
assert "Buy cheapest" in page
# Trailhead landing structure from ShipDeal v2.pdf
assert "THE TRAILHEAD" in page
assert "NEW · IN STOCK · LANDED PRICE FOR GB" in page
assert "Pick your country, pick a part, one search." in page
assert "NEW ONLY" in page and "STOCK, WITH EVIDENCE" in page
assert "THE REAL PRICE" in page and "A LINK THAT LOADS" in page
assert "RETAILER RING" in page and "probikesupply" in page
assert "NO USED · NO DEAD LINKS · NO GENERIC SEARCH JUNK" in page
# Trailhead design tokens are applied to the rendered page
assert "#F2EDE3" in page and "#B94A26" in page and "#16211C" in page
assert "Big+Shoulders" in page and "DM+Mono" in page
print("dashboard tests OK")
