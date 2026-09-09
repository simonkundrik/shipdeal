"""RED: landed_row computes the true delivered price per country for a DB row."""
from landed import landed_row
from regions import country_info

row = {"price_gbp": 100.0, "shipping_gbp": 25.0}

gb = country_info("GB")       # vat 0, duty 0
assert abs(landed_row(row, gb) - 125.0) < 0.01

us = country_info("US")       # goods 100 < de_minimis 640 -> no duty; vat 0
assert abs(landed_row(row, us) - 125.0) < 0.01

au = country_info("AU")       # GST 10% on taxable
assert abs(landed_row(row, au) - 137.5) < 0.01

# shipping unknown -> treat as 0 (flagged by caller), not crash
row2 = {"price_gbp": 120.0, "shipping_gbp": None}
assert abs(landed_row(row2, gb) - 120.0) < 0.01
print("landed-row tests OK")
