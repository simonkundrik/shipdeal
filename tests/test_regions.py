"""RED: retailer ring has all live-scrapable stores plus a scrapable flag and ships fallback."""
from regions import RETAILERS, REGIONS, retailers_for, shipping_hint

assert "chainreactioncycles" in RETAILERS
assert "icancycling" in RETAILERS
assert "winspace" in RETAILERS
assert "yoeleo" in RETAILERS
assert "probikesupply" in RETAILERS
# every retailer carries a scrapable flag (True/False) and a ships hint for any region
for name, cfg in RETAILERS.items():
    assert "scrapable" in cfg
    assert cfg["scrapable"] in (True, False)
assert shipping_hint("probikesupply", "XX") == "shipping unknown"
assert "Global" in REGIONS and retailers_for("EU/UK")
print("regions tests OK")
