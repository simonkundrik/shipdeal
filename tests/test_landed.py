"""Landed tests — origin-aware model (replaces the old double-taxing landed_cost tests)."""
from landed import landed

# domestic GB: listed price unchanged, VAT already inside
L = landed(519.0, "huntbikewheels", "GB")
assert L["total_gbp"] == 519.0 and L["vat"] == 0.0 and "no border" in L["duty_note"]

# intra-EU differs by VAT ratio: SE (25%) > DE (19%) — the whole feature
assert landed(429.0, "probikesupply", "SE")["total_gbp"] > landed(429.0, "probikesupply", "DE")["total_gbp"]

# EU retailer -> GB crosses customs: duty + 20% VAT + £12 clearance
L2 = landed(429.0, "probikesupply", "GB")
assert L2["crossing"] and L2["dutiable"] and L2["duty"] > 0 and L2["clearance"] == 12
assert "import duty" in L2["duty_note"]

# cheap line under de-minimis: VAT only, no duty
L3 = landed(41.99, "chainreactioncycles", "GB")
assert L3["duty"] == 0 and L3["vat"] > 0 and "threshold" in L3["duty_note"]

# retailer not delivering to the zone is dropped, never priced at zero
L4 = landed(519.0, "yoeleo", "GB")
assert L4["serves"] is False and L4["total_gbp"] is None
print("landed tests OK")
