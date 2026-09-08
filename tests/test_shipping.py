"""RED: delivery cost must be included (free-over thresholds, unknown flagged)."""
from regions import delivery_cost_gbp, POSTAGE

# probikesupply EU/UK: flat delivery, no free-over -> always pay
cost, free = delivery_cost_gbp("probikesupply", "EU/UK", 100)
assert cost is not None and cost > 0 and free is None

# CRC EU/UK: free delivery (free_over 0 -> cost 0)
cost2, free2 = delivery_cost_gbp("chainreactioncycles", "EU/UK", 50)
assert cost2 == 0 and free2 == 0

# unknown retailer -> cost None (flagged, never silently ignored)
cost3, _ = delivery_cost_gbp("nonexistent_shop", "EU/UK", 100)
assert cost3 is None

# factory-direct China brands ship worldwide -> EU/UK delivery must be priced, not unknown
cost4, free4 = delivery_cost_gbp("icancycling", "EU/UK", 123.24)
assert cost4 is not None and cost4 > 0
cost5, _ = delivery_cost_gbp("winspace", "EU/UK", 156.0)
assert cost5 is not None and cost5 > 0
cost6, _ = delivery_cost_gbp("yoeleo", "EU/UK", 272.22)
assert cost6 is not None and cost6 > 0

# every entry carries cost_gbp + free_over_gbp
for retail, by_region in POSTAGE.items():
    for region, e in by_region.items():
        assert "cost_gbp" in e and "free_over_gbp" in e
print("shipping tests OK")
