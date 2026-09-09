"""Landed-row tests — new signature landed_row(row, country) reads the retailer off the row."""
from landed import landed_row

row = {"price_gbp": 519.0, "retailer": "huntbikewheels"}
assert landed_row(row, "GB")["total_gbp"] == 519.0  # domestic GB unchanged

row2 = {"price_gbp": 120.0, "retailer": "probikesupply"}  # NL -> GB crossing
L = landed_row(row2, "GB")
assert L["vat"] > 0 and L["crossing"] and L["serves"] is True

row3 = {"price_gbp": 519.0, "retailer": "yoeleo"}  # no postage for GB zone
assert landed_row(row3, "GB")["serves"] is False
print("landed-row tests OK")
