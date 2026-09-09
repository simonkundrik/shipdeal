"""RED: retailer collection pages per component exist and return list URLs."""
from regions import collections_for

assert "/collections/" in collections_for("probikesupply", "fork")[0]
assert "/collections/" in collections_for("probikesupply", "tires")[0]
assert "/collections/" in collections_for("probikesupply", "rear_shock")[0]
assert collections_for("probikesupply", "wheelset")
assert "/search" in collections_for("winspace", "wheelset")[0]
assert collections_for("probikesupply", "fork")  # non-empty
print("collections tests OK")
