"""Compat-gate tests — pin the 8 Trailhead checks on build picks."""
from compat import compat_issues


def _pick(**kw):
    base = {"brand": "Fox", "price_gbp": 425.1, "retailer": "probikesupply",
            "wheel": "29", "travel": 170, "stock": "in_stock"}
    base.update(kw)
    return base


# coherent enduro build -> duty warms only (EU retailers crossing to GB)
picks = {
    "fork": _pick(brand="Fox", retailer="probikesupply"),
    "frame": _pick(brand="Dengfu", retailer="winspace"),
    "wheelset": _pick(brand="Hunt", retailer="huntbikewheels"),
    "tires": _pick(brand="Maxxis", retailer="probikesupply"),
}
issues = compat_issues("enduro", picks, "GB")
# only dutiable warns (intra-customs crossing); no wheel/travel/stock/serve errors
assert all(i["level"] in ("warn",) for i in issues), issues

# mismatch build: 27.5 wheel, DH fork 200 on enduro preset, unknown stock, non-serving retailer
picks2 = {
    "fork": _pick(brand="RockShox", retailer="yoeleo", wheel="27.5", travel=200, stock="unknown"),
    "frame": _pick(brand="Dengfu", retailer="winspace", wheel="29"),
    "wheelset": _pick(brand="Winspace", retailer="winspace", wheel="27.5"),
}
i2 = compat_issues("enduro", picks2, "GB")
levels = {i["level"] for i in i2}
assert "error" in levels, i2  # wheel clash + retailer not serving
assert any(i["title"] == "Wheel size mismatch" for i in i2)
assert any(i["title"] == "Retailer does not deliver" for i in i2)
assert any(i["level"] == "warn" and i["title"] == "Part not confirmed in stock" for i in i2)

# empty build -> no 'ok' (build must be non-empty)
assert compat_issues("enduro", {}, "GB") == []
print("compat tests OK")
