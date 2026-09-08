"""Curated MTB build catalogue: components, credible brands, budgets, style defaults."""
STYLE_DEFAULTS = {
    "xc":       {"fork_travel": 120, "wheel": "29", "rear_travel": 120},
    "enduro":   {"fork_travel": 170, "wheel": "29", "rear_travel": 170},
    "freeride": {"fork_travel": 180, "wheel": "27.5", "rear_travel": 180},
    "downhill": {"fork_travel": 200, "wheel": "29", "rear_travel": 200},
    "ebike":    {"fork_travel": 170, "wheel": "29", "rear_travel": 170},
}

# component -> credible searches + budgets. wheel/travel True when spec must match the style.
COMPONENTS = {
    "frame":        {"budget": 1400, "min": 300, "max": 1400, "wheel": True, "travel": True,
                     "brands": "ICAN,Trifox,Dengfu"},
    "fork":         {"budget": 600, "min": 120, "max": 600, "wheel": True, "travel": True,
                     "brands": "RockShox,Marzocchi,Fox,Manitou", "strict_stock": True},
    "rear_shock":   {"budget": 450, "min": 90, "max": 450, "travel": False,
                     "brands": "Marzocchi,Fox,RockShox,Cane Creek"},
    "wheelset":     {"budget": 550, "min": 130, "max": 800, "wheel": True,
                     "brands": "Hunt,Winspace,Yoeleo,Novatec"},
    "tires":        {"budget": 90, "min": 20, "max": 120, "wheel": True,
                     "brands": "Maxxis,Kenda,Continental"},
    "drivetrain":   {"budget": 340, "min": 120, "max": 500, "brands": "Box,Ltwoo,ZTTO,Shimano"},
    "brakes":       {"budget": 230, "min": 50, "max": 350, "brands": "TRP,Formula,Trickstuff,Magura"},
    "cockpit":      {"budget": 130, "min": 30, "max": 200, "brands": "Renthal,Deity,ZTTO"},
    "pedals":       {"budget": 45, "min": 8, "max": 60, "brands": "VP,Wellgo,OneUp"},
    "saddle_post":  {"budget": 95, "min": 20, "max": 120, "brands": "Ergon,WTB,Bolany"},
}


def brand_search(component, brand):
    """Query string for a component+brand."""
    return f"{component} {brand.replace('-', ' ')} mtb"


def style_defaults(style):
    return STYLE_DEFAULTS.get(style, STYLE_DEFAULTS["enduro"])
