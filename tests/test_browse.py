"""RED: browse renders DB rows with landed cost (net+ship+duty+VAT+clearance) per country."""
from app import row_line, browse_render  # noqa: F401

row = {"component": "fork", "brand": "Marzocchi", "name": "Bomber Z1", "price": "545",
       "currency": "USD", "price_gbp": 425.1, "stock": "in_stock",
       "retailer": "probikesupply", "image": "", "url": "http://x/fork",
       "landed": {"label": "£471.70", "breakdown": "net £304.91 + ship £14.00 + duty + VAT "
                  "+ clearance £12.00", "duty_note": "import duty + 20% VAT applied",
                  "days": 4, "origin": "NL", "total_gbp": 471.70}}
line = row_line(row, "GB")
assert "£471.70" in line and "BUY CHEAPEST" in line and "Add to build" in line
assert "import duty" in line and "(NL)" in line

page = browse_render(["fork"], "GB", rows=[row])
assert "Add to build" in page and "My Build" in page
assert "SHIPDEAL" in page and "Parts that make it to the trailhead" in page
print("browse tests OK")
