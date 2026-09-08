"""RED: recompute_delivery updates stored rows with delivery-inclusive totals."""
from populate import recompute_delivery

db = {"products": [{"component": "fork", "retailer": "icancycling",
                    "price_gbp": 123.24, "shipping_gbp": None, "total_gbp": None}]}
db = recompute_delivery(db, "EU/UK")
r = db["products"][0]
assert r["shipping_gbp"] == 30.0
assert abs(r["total_gbp"] - 153.24) < 0.01

# retailer with no POSTAGE for the region -> delivery unknown (None), total None
db2 = {"products": [{"retailer": "some_shop", "price_gbp": 100.0,
                     "shipping_gbp": None, "total_gbp": None}]}
db2 = recompute_delivery(db2, "EU/UK")
assert db2["products"][0]["shipping_gbp"] is None
assert db2["products"][0]["total_gbp"] is None
print("recompute tests OK")
