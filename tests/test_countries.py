"""Country tests — point at countries.COUNTRY_INFO (fx renamed to gbp_to_local)."""
from countries import COUNTRY_INFO, country_info, money, tax_line, groups, REGION_ALIAS

assert len(COUNTRY_INFO) == 17
required = {"vat_rate", "duty_rate", "duty_free_gbp", "tax_free_gbp", "clearance_fee_gbp",
            "currency", "gbp_to_local", "customs", "zone"}
for code, info in COUNTRY_INFO.items():
    assert required <= info.keys()
assert country_info("GB")["currency"] == "GBP"
assert country_info("GB")["duty_rate"] == 0.041
assert country_info("DE")["vat_rate"] == 0.19
assert money("SE", 100).endswith(" kr")
assert money("GB", 1185.39) == "£1,185.39"
assert "duty from the first NOK" in tax_line("NO")
assert REGION_ALIAS["EU/UK"] == "GB"
assert any(name == "Germany" for _, items in groups() for cc, name in items if cc == "DE")
print("countries tests OK")
