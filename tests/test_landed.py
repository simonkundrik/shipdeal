"""RED: landed cost — listed price -> FX -> ship -> duty -> VAT -> clearance."""
from landed import landed_cost

# below de-minimis: no duty/clearance; goods 100*0.80=80 + ship 25 = 105, VAT 20%
c = landed_cost(list_price=100, currency="USD", fx=0.80, ship=25, duty_rate=0.0,
                vat_rate=0.20, de_minimis=135, clearance=0)
assert abs(c - (80 + 25) * 1.20) < 0.01   # = 126.0

# above de-minimis: duty on goods, VAT on taxable, clearance fee
c2 = landed_cost(list_price=500, currency="USD", fx=0.80, ship=25, duty_rate=0.04,
                 vat_rate=0.20, de_minimis=135, clearance=10)
goods_gbp = 400.0
base = goods_gbp + 25            # 425
duty = goods_gbp * 0.04          # 16
vat = (base + duty) * 0.20       # 88.2
expected = base + duty + vat + 10
assert abs(c2 - expected) < 0.2  # ~539.2
assert landed_cost(list_price=1, currency="GBP", fx=1.0, ship=0,
                   duty_rate=0, vat_rate=0, de_minimis=135, clearance=0) == 1.0
print("landed tests OK")
