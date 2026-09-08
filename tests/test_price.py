"""RED: nail_price must return the real listing price (545 USD), NOT the $199 shipping fee."""
import sys
import httpx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from price import nail_price

p = {"id": "fork", "name": "fork", "budget_gbp": 600, "min_price": 120, "max_price": 600}
d = {"url": "https://www.probikesupply.com/products/"
     "marzocchi-bomber-z1-coil-suspension-fork-27-5-170-mm-15-x-110-mm-44-mm-offset-"
     "matte-black-grip-sweep-adjust",
     "title": "Marzocchi Bomber Z1 Coil", "brand": "Marzocchi", "note": ""}
ok = nail_price(d, p, httpx.Client(timeout=75))
assert ok is True
assert d["price"] == 545 and d["currency"] == "USD"
assert abs(d["price_gbp"] - 425.1) < 0.5  # 545 -> ~425 GBP, NOT 199 -> ~155
print("price tests OK")
