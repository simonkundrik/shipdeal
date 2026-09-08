"""RED: browse renders DB rows with delivery included in the total (price + shipping)."""
from app import row_line, browse_render  # noqa: F401

row = {"component": "fork", "brand": "Marzocchi", "name": "Bomber Z1", "price": "545",
       "currency": "USD", "price_gbp": 425.1, "shipping_gbp": 25.0, "total_gbp": 450.1,
       "stock": "in_stock", "retailer": "probikesupply", "image": "", "url": "http://x/fork"}
line = row_line(row)
assert "425.1" in line and "25" in line and "450.1" in line
assert "delivery" in line.lower()

# delivery-unknown rows must flag it rather than pretend it's free
row2 = {"component": "fork", "brand": "Fox", "price": "545", "currency": "USD",
        "price_gbp": 425.1, "shipping_gbp": None, "total_gbp": None,
        "stock": "in_stock", "retailer": "some_shop", "image": "", "url": "http://x/f2"}
line2 = row_line(row2)
assert "delivery unknown" in line2.lower()

page = browse_render(["fork"], "EU/UK", rows=[row, row2])
assert "Add to build" in page and "My Build" in page
print("browse tests OK")
