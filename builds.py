"""Build cart: choose one part per component -> assemble a bike from cheapest sellers."""
import json
from dataclasses import dataclass, asdict
from pathlib import Path

BUILDS_FILE = Path(__file__).parent / "data" / "builds.json"


@dataclass
class Pick:
    component: str
    brand: str
    price: str
    currency: str
    price_gbp: float
    url: str
    image: str = ""
    ships: str = ""
    total_gbp: float = None  # price + delivery; None -> falls back to price_gbp


def load():
    return BUILDS_FILE.read_text() if BUILDS_FILE.exists() else "{}"


def save(picks: dict):
    BUILDS_FILE.parent.mkdir(exist_ok=True)
    BUILDS_FILE.write_text(json.dumps(picks, indent=2))


def total(picks: dict):
    """Cart total using delivery-inclusive total_gbp when present, else price_gbp."""
    return round(sum((p.get("total_gbp") if p.get("total_gbp") is not None else p.get("price_gbp") or 0)
                     for p in picks.values()), 2)


def add(picks: dict, pick: Pick):
    picks[pick.component] = asdict(pick)
    return picks
