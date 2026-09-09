"""Build compatibility gate — flags a picked build against the style preset.

Runs the 8 Trailhead checks on a `builds` picks dict (component -> pick dict). Each issue is
{level: "error"|"warn"|"ok", title, detail, keys: [component keys]} where `keys` drives the
callout colour (#D9634A) in the build panel.
"""
from __future__ import annotations

from catalogue import STYLE_DEFAULTS
from countries import country_info
from landed import landed

RELEVANT_WHEEL = ("frame", "fork", "wheelset", "tires")


def _get(picks, component, field):
    p = picks.get(component)
    return p.get(field) if p else None


def _landed(pick, country):
    """landed() for one pick; safe even if the retailer is unknown/missing."""
    try:
        return landed(pick.get("price_gbp") or 0.0, pick.get("retailer") or "", country)
    except Exception:  # noqa: BLE001 - never let a bad retailer crash the panel
        return {"serves": True, "dutiable": False}


def compat_issues(style, picks, country):
    """Return the list of compatibility issues for a build.

    `picks` is the builds dict (component -> pick with brand, price_gbp, retailer, wheel,
    travel, stock). `style` is one of STYLE_DEFAULTS keys. `country` is ISO-2.
    """
    preset = STYLE_DEFAULTS.get(style, STYLE_DEFAULTS["enduro"])
    issues = []

    # 1. error: wheel sizes differ across frame/fork/wheelset/tires
    wheels = {c: _get(picks, c, "wheel") for c in RELEVANT_WHEEL if _get(picks, c, "wheel")}
    wheel_set = sorted(set(w for w in wheels.values() if w))
    if len(wheel_set) > 1:
        detail = "Wheel sizes differ across " + ", ".join(f"{c}={w}" for c, w in wheels.items()) + "."
        issues.append({"level": "error", "title": "Wheel size mismatch",
                       "detail": detail, "keys": list(wheels.keys())})

    # 2. warn: the single wheel size != style preset wheel
    elif wheel_set:
        w = wheel_set[0]
        if w != preset["wheel"]:
            issues.append({"level": "warn", "title": "Wheel size off style preset",
                           "detail": f"{w}in wheels vs {preset['wheel']}in {style} preset.",
                           "keys": list(wheels.keys())})

    # 3. fork travel vs style preset: warn >20mm out, error >40mm over
    ft = _get(picks, "fork", "travel")
    if ft:
        pft = preset["fork_travel"]
        if ft > pft + 40:
            issues.append({"level": "error", "title": "Fork travel over style limit",
                           "detail": f"fork {ft}mm vs {pft}mm {style} preset — over by {ft - pft}mm (>40mm).",
                           "keys": ["fork"]})
        elif abs(ft - pft) > 20:
            issues.append({"level": "warn", "title": "Fork travel off style preset",
                           "detail": f"fork {ft}mm vs {pft}mm {style} preset.",
                           "keys": ["fork"]})

    # 4. warn: fork travel vs frame rear travel more than 20mm apart
    rt = preset["rear_travel"]
    if ft and abs(ft - rt) > 20:
        issues.append({"level": "warn", "title": "Fork / rear travel imbalance",
                       "detail": f"fork {ft}mm vs rear {rt}mm — {abs(ft - rt)}mm apart (>20mm).",
                       "keys": ["fork", "frame"]})

    # 5. warn: any pick whose stock is not in_stock
    for c, p in picks.items():
        st = p.get("stock") or ""
        if st and st != "in_stock":
            issues.append({"level": "warn", "title": "Part not confirmed in stock",
                           "detail": f"{p.get('brand', '')} ({c}) stock: {st}.",
                           "keys": [c]})

    info = country_info(country)

    # 6. error: retailer does not serve the country
    for c, p in picks.items():
        retailer = p.get("retailer") or ""
        if retailer and not _landed(p, country).get("serves", True):
            issues.append({"level": "error", "title": "Retailer does not deliver",
                           "detail": f"{retailer} does not serve {info.get('name', country)} — "
                                     f"{p.get('brand', '')} ({c}).",
                           "keys": [c]})

    # 7. warn: dutiable line (name retailers + VAT rate)
    vat_pct = round(info.get("vat_rate", 0.0) * 100)
    for c, p in picks.items():
        retailer = p.get("retailer") or ""
        if retailer and _landed(p, country).get("dutiable"):
            issues.append({"level": "warn", "title": "Import duty applies",
                           "detail": f"{retailer} line for {p.get('brand', '')} triggers duty "
                                     f"({vat_pct}% VAT).",
                           "keys": [c]})

    # 8. ok — only when build is non-empty and checks 1-7 found nothing
    if picks and not any(i["level"] in ("error", "warn") for i in issues):
        issues.append({"level": "ok", "title": "No conflicts",
                       "detail": "Build is coherent.", "keys": []})

    return issues
