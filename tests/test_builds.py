"""RED: build cart — add a pick per component and compute total; persists builds.json."""
import json
from builds import Pick, add, total, load, save, BUILDS_FILE

picks = {}
add(picks, Pick(component="fork", brand="Marzocchi", price="545", currency="USD",
                price_gbp=425.1, url="http://x/fork"))
add(picks, Pick(component="tires", brand="Maxxis", price="78", currency="USD",
                price_gbp=60.84, url="http://x/tires"))
assert len(picks) == 2
assert abs(total(picks) - 485.94) < 0.01
assert BUILDS_FILE.name == "builds.json"
save(picks)
assert json.loads(load())["fork"]["brand"] == "Marzocchi"
print("builds OK")
