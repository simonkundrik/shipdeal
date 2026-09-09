"""RED: COUNTRY_INFO has 17 countries with vat/duty/de-minimis/clearance/currency/fx."""
from regions import COUNTRY_INFO, country_info

assert len(COUNTRY_INFO) == 17
required = {"vat_rate", "duty_rate", "de_minimis", "clearance_fee", "currency", "fx"}
for code, info in COUNTRY_INFO.items():
    assert required <= info.keys()
assert country_info("GB")["currency"] == "GBP"
assert country_info("US")["duty_rate"] > 0
assert country_info("DE")["vat_rate"] >= 0.19
print("countries tests OK")
