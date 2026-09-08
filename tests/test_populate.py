"""RED: populate — total includes delivery, dedupe by (url, retailer), DB save/load."""
from populate import total_with_delivery, add_row, save_products, load_products, PRODUCTS_FILE

assert total_with_delivery(400.0, 25.0) == 425.0   # flat delivery added
assert total_with_delivery(400.0, 0.0) == 400.0    # free delivery
assert total_with_delivery(400.0, None) is None    # delivery unknown -> total unknown (flagged)

db = {"products": [], "scraped_at": None}
db = add_row(db, {"url": "u1", "retailer": "r1", "component": "fork"})
db = add_row(db, {"url": "u1", "retailer": "r1", "component": "fork"})  # duplicate -> dedupe
db = add_row(db, {"url": "u2", "retailer": "r1", "component": "fork"})  # different url -> kept
assert len(db["products"]) == 2

assert PRODUCTS_FILE.name == "products.json"
save_products(db)
assert load_products()["products"] == db["products"]
print("populate tests OK")
