"""Landed-cost, origin-aware — the Trailhead pricing model.

A listed price is VAT-inclusive in the retailer's home market; the shopper pays the origin-VAT
stripped, destination-VAT applied, plus duty and clearance when a customs border is crossed and
the goods pass the de-minimis threshold. This re-exports the reference `landed_v2` module so
existing callers (tests/test_landed.py, tests/test_landed_row.py) keep importing `landed`.
"""
from landed_v2 import landed, landed_row, sort_by_landed  # noqa: F401
