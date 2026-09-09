"""Pins the behaviour the Trailhead design depends on. Same style as tests/test_landed.py."""
from countries import money, tax_line
from landed_v2 import landed


def test_domestic_uk_keeps_the_listed_price():
    L = landed(519.0, "huntbikewheels", "GB")            # GB shop -> GB shopper
    assert L["total_gbp"] == 519.0
    assert L["duty_note"] == "no border to cross"
    assert L["vat"] == 0.0                                # VAT already inside the listed price


def test_same_listing_costs_differently_across_the_eu():
    de = landed(429.0, "probikesupply", "DE")["total_gbp"]   # 19% VAT
    se = landed(429.0, "probikesupply", "SE")["total_gbp"]   # 25% VAT
    assert se > de                                            # this is the whole feature


def test_eu_to_uk_crosses_customs_and_picks_up_duty_and_clearance():
    L = landed(429.0, "probikesupply", "GB")
    assert L["crossing"] and L["dutiable"]
    assert L["duty"] > 0 and L["clearance"] == 12
    assert "import duty" in L["duty_note"]


def test_cheap_line_under_de_minimis_pays_vat_but_no_duty():
    L = landed(41.99, "chainreactioncycles", "GB")
    assert L["duty"] == 0 and L["clearance"] == 0
    assert L["vat"] > 0
    assert "duty threshold" in L["duty_note"]


def test_retailer_that_does_not_deliver_is_not_priced_at_zero():
    L = landed(519.0, "yoeleo", "GB")                     # no ZONE_POSTAGE entry
    assert L["serves"] is False and L["total_gbp"] is None


def test_no_duty_free_threshold_reads_sensibly():
    assert "duty from the first NOK" in tax_line("NO")
    assert money("SE", 100).endswith(" kr")
    assert money("GB", 1185.39) == "\u00a31,185.39"
