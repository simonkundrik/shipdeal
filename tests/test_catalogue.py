"""RED: catalogue module must exist with fork strict_stock and style defaults."""
from catalogue import COMPONENTS, style_defaults

assert COMPONENTS["fork"]["strict_stock"] is True
assert COMPONENTS["fork"]["travel"] is True
assert style_defaults("downhill")["wheel"] == "29"
assert style_defaults("freeride")["wheel"] == "27.5"
assert style_defaults("xc")["fork_travel"] == 120
assert style_defaults("enduro")["fork_travel"] == 170
print("catalogue tests OK")
