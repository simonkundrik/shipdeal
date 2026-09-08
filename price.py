"""Exact price nailing: use the authoritative (modal, noise-rejected) listing price.

authoritative_price() from the mtb_deals toolchain returns the real product price and rejects
shipping-fee/financing/eligible noise, so a $199 'shipping fee' is never mistaken for a $545 fork.
Returns False when no real price exists on the page (drop the candidate rather than guess).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "mtb_deals"))
from scraper import authoritative_price  # noqa: E402


def nail_price(d, part, client):
    """Set d['price']/d['currency']/d['price_gbp'] to the authoritative listing price.
    Returns False if no real price could be nailed (candidate must be dropped)."""
    authoritative_price(d, part, client)
    return bool(d.get("price_gbp"))
