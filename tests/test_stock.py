"""RED: stock checker — forks strictly in stock, others reject only confirmed out-of-stock."""
from stock_checker import check_stock, passes_stock, STRONG_IN, STRONG_OUT

assert check_stock("Only 1 left in stock.", "fork") == ("in_stock", "left in stock")
assert check_stock("OUT OF STOCK", "fork")[0] == "out_of_stock"
assert check_stock("", "wheelset")[0] == "unknown"
# Amazon boilerplate "currently unavailable" must NOT override a decisive "Add to cart"
assert check_stock("Add to cart. Product currently unavailable.", "fork")[0] == "in_stock"
assert passes_stock("unknown", "wheelset") is True      # loosened for non-fork
assert passes_stock("out_of_stock", "wheelset") is False
assert passes_stock("in_stock", "fork") is True
assert passes_stock("unknown", "fork") is False          # forks must be confirmed in stock
assert passes_stock("out_of_stock", "fork") is False
assert "left in stock" in STRONG_IN and "sold out" in STRONG_OUT
print("stock tests OK")
