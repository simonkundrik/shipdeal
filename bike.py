"""Python port of bikeArt() from design/ShipDeal v2.dc.html (lines 658-817).

Geometry/look data is read from bike_geometry.json (snake_case), the
rendering math mirrors the authoritative JS implementation.
"""
import json
import math
import os

_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bike_geometry.json")
with open(_JSON_PATH, "r", encoding="utf-8") as _f:
    GEO = json.load(_f)

GEO_MM = GEO["geo_mm"]
LOOK = GEO["look"]
TUBE_WIDTHS = GEO["tube_widths_mm"]
SLOTS = GEO["slots"]

S = 0.2865
GROUND_Y = 470


def _r(v):
    return round(v * 10) / 10


def _tube_str(a, b, w1, w2, P):
    A = P(a)
    B = P(b)
    dx = B[0] - A[0]
    dy = B[1] - A[1]
    L = math.hypot(dx, dy) or 1
    nx = -dy / L
    ny = dx / L
    W1 = w1 * S
    W2 = w2 * S

    def o(p, w, s):
        return (_r(p[0] + nx * w / 2 * s), _r(p[1] + ny * w / 2 * s))

    pts = [o(A, W1, 1), o(B, W2, 1), o(B, W2, -1), o(A, W1, -1)]
    return " ".join(f"{p[0]},{p[1]}" for p in pts)


def _ticks(cx, cy, r0, r1, n):
    out = []
    for i in range(n):
        a = (i / n) * math.pi * 2
        out.append((
            _r(cx + math.cos(a) * r0), _r(cy + math.sin(a) * r0),
            _r(cx + math.cos(a) * r1), _r(cy + math.sin(a) * r1),
        ))
    return out


def _dress(picked, fill):
    if picked:
        return {"fill": fill, "stroke": "#0F1614", "dash": None, "op": 1}
    return {"fill": "none", "stroke": "#5C6A61", "dash": "6 5", "op": 0.7}


def _dress_attrs(dress):
    attrs = f'fill="{dress["fill"]}" stroke="{dress["stroke"]}" opacity="{dress["op"]}"'
    if dress["dash"]:
        attrs += f' stroke-dasharray="{dress["dash"]}"'
    return attrs


def _polygon(points, dress, extra=""):
    return f'<polygon points="{points}" {_dress_attrs(dress)}{extra}/>'


def bike_svg(style, picks):
    g = GEO_MM.get(style, GEO_MM["enduro"])
    tire = g["tire"]
    wb = g["wb"]
    ha = g["ha"]
    travel = g["travel"]
    seat_tube = g["seat_tube"]
    post = g["post"]
    dual = g["dual"]
    motor_on = g["motor"]

    tPx = tire * S
    wbPx = wb * S
    ox = tPx + (1000 - wbPx - 2 * tPx) / 2

    def X(mm):
        return ox + mm * S

    def Y(mm):
        return GROUND_Y - mm * S

    def P(pt):
        return (_r(X(pt[0])), _r(Y(pt[1])))

    def pick(k):
        return picks.get(k) or picks.get(k.replace("_post", ""))

    def brand_look(k, table):
        p = pick(k)
        brand = p["brand"] if p else None
        return table.get(brand, table["_default"])

    def tube(a, b, w1, w2):
        return _tube_str(a, b, w1, w2, P)

    bb = (434, 345)
    rear_ax = (0, tire)
    front_ax = (wb, tire)
    rad = math.radians(ha)
    ux, uy = -math.cos(rad), math.sin(rad)
    fork_len = travel + 380

    def f_at(t):
        return (wb + ux * fork_len * t, tire + uy * fork_len * t)

    crown = f_at(1)
    ht_bot = (crown[0] + ux * 14, crown[1] + uy * 14)
    ht_top = (crown[0] + ux * 150, crown[1] + uy * 150)
    stem_b = (ht_top[0] + ux * 55, ht_top[1] + uy * 55)
    bar_pt = (stem_b[0] + 78, stem_b[1] + 20)
    sdx, sdy = -math.cos(math.radians(76)), math.sin(math.radians(76))
    seat_top = (bb[0] + sdx * seat_tube, bb[1] + sdy * seat_tube)
    saddle_mm = (seat_top[0] + sdx * post, seat_top[1] + sdy * post)
    pivot = (bb[0] + 60, bb[1] + 75)
    ss_top = (bb[0] + sdx * seat_tube * 0.68, bb[1] + sdy * seat_tube * 0.68)
    rock_b = (ss_top[0] + 78, ss_top[1] - 34)
    dt_mid = (bb[0] + (ht_bot[0] - bb[0]) * 0.42, bb[1] + (ht_bot[1] - bb[1]) * 0.42)
    ped = (bb[0] + 152, bb[1] - 92)

    rax, ray = P(rear_ax)
    fax, fay = P(front_ax)
    tireR = _r(tPx)

    tl = brand_look("tires", LOOK["tires"])
    cw = tl["casing_mm"]
    knob = tl["knob"]
    casR = _r(tireR - cw / 2)
    rimR = _r(tireR - cw - 5)
    tread = _ticks(rax, ray, tireR - 1, casR + 1, knob) + _ticks(fax, fay, tireR - 1, casR + 1, knob)
    spokes = _ticks(rax, ray, 11, rimR - 4, 18) + _ticks(fax, fay, 11, rimR - 4, 18)

    fork_l = brand_look("fork", LOOK["fork"])
    rotor_mm = brand_look("brakes", LOOK["brakes_rotor_mm"])
    rotorR = _r(rotor_mm / 2 * S)
    cog_n = brand_look("drivetrain", LOOK["drivetrain_cogs"])
    ped_w = brand_look("pedals", LOOK["pedals_plate_mm"])

    ring_x, ring_y = P(bb)
    ring_r = _r(72 * S)
    cogs = [(rax, ray, _r(30 - i * (22 / cog_n))) for i in range(cog_n)]
    p1 = (_r(rax + 30), _r(ray + 34))
    p2 = (_r(rax + 10), _r(ray + 60))
    sad = P(saddle_mm)

    parts = []

    # -- wheels --
    tires_picked = bool(pick("tires"))
    casing_dress = _dress(tires_picked, "none")
    casing_stroke = "#2C3335" if tires_picked else "#5C6A61"
    tread_color = "#454F51" if tires_picked else "#5C6A61"
    wheelset_color = brand_look("wheelset", LOOK["wheelset"])
    wheelset_picked = bool(pick("wheelset"))
    rim_dress = _dress(wheelset_picked, wheelset_color)

    for (wcx, wcy) in ((rax, ray), (fax, fay)):
        parts.append(
            f'<circle cx="{wcx}" cy="{wcy}" r="{casR}" fill="{casing_dress["fill"]}" '
            f'stroke="{casing_stroke}" opacity="{casing_dress["op"]}"'
            + (f' stroke-dasharray="{casing_dress["dash"]}"' if casing_dress["dash"] else "")
            + "/>"
        )
    for (x1, y1, x2, y2) in tread:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{tread_color}"/>')
    for (x1, y1, x2, y2) in spokes:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{rim_dress["stroke"]}" opacity="{rim_dress["op"]}"/>')
    for (wcx, wcy) in ((rax, ray), (fax, fay)):
        parts.append(
            f'<circle cx="{wcx}" cy="{wcy}" r="{rimR}" fill="none" stroke="{rim_dress["stroke"]}" '
            f'opacity="{rim_dress["op"]}"'
            + (f' stroke-dasharray="{rim_dress["dash"]}"' if rim_dress["dash"] else "")
            + "/>"
        )
        parts.append(f'<circle cx="{wcx}" cy="{wcy}" r="11" fill="{rim_dress["fill"] if rim_dress["fill"] != "none" else "#0F1614"}" opacity="{rim_dress["op"]}"/>')

    # -- brake rotor + slots + caliper (front wheel) --
    brakes_dress = _dress(bool(pick("brakes")), "#C6CCC8")
    parts.append(f'<circle cx="{fax}" cy="{fay}" r="{rotorR}" {_dress_attrs(brakes_dress)}/>')
    slots = _ticks(fax, fay, rotorR - 3, rotorR - 11, 16)
    for (x1, y1, x2, y2) in slots:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{brakes_dress["stroke"]}" opacity="{brakes_dress["op"]}"/>')
    caliper_pts = f'{_r(fax - 30)},{_r(fay - 16)} {_r(fax - 12)},{_r(fay - 22)} {_r(fax - 8)},{_r(fay + 8)} {_r(fax - 26)},{_r(fay + 14)}'
    parts.append(_polygon(caliper_pts, brakes_dress))

    # -- cog rings (drivetrain) --
    drive_dress = _dress(bool(pick("drivetrain")), "#8E9A94")
    for (ccx, ccy, cr) in cogs:
        parts.append(f'<circle cx="{ccx}" cy="{ccy}" r="{cr}" {_dress_attrs(drive_dress)}/>')

    # -- frame --
    frame_brand = (pick("frame") or {}).get("brand")
    frame_fill = LOOK["frame"].get(frame_brand, LOOK["frame"]["_default"])
    frame_dress = _dress(bool(pick("frame")), frame_fill)
    frame_tubes = [
        tube(seat_top, ht_top, *TUBE_WIDTHS["seat_to_head"]),
        tube(bb, ht_bot, *TUBE_WIDTHS["down_tube"]),
        tube(bb, seat_top, *TUBE_WIDTHS["seat_tube"]),
        tube(ht_bot, ht_top, *TUBE_WIDTHS["head_tube"]),
        tube(pivot, rear_ax, *TUBE_WIDTHS["chainstay"]),
        tube(rear_ax, rock_b, *TUBE_WIDTHS["seatstay"]),
        tube(rock_b, ss_top, *TUBE_WIDTHS["rocker"]),
    ]
    for pts in frame_tubes:
        parts.append(_polygon(pts, frame_dress))

    # -- fork --
    fork_picked = bool(pick("fork"))
    fork_dress = _dress(fork_picked, fork_l["lower"])
    parts.append(_polygon(tube(front_ax, f_at(0.66), *TUBE_WIDTHS["fork_lower"]), fork_dress))
    stanch_color = fork_l["stanchion"] if fork_picked else "none"
    stanch_dress = dict(fork_dress)
    stanch_dress["fill"] = stanch_color
    parts.append(_polygon(tube(f_at(0.62), crown, *TUBE_WIDTHS["fork_stanchion"]), stanch_dress))
    if dual:
        parts.append(_polygon(tube((crown[0] - 55, crown[1]), (crown[0] + 55, crown[1]), 34, 34), fork_dress))
        parts.append(_polygon(tube((ht_top[0] - 55, ht_top[1]), (ht_top[0] + 55, ht_top[1]), 30, 30), fork_dress))
    else:
        parts.append(_polygon(tube((crown[0] - 58, crown[1] - 6), (crown[0] + 46, crown[1] + 8), *TUBE_WIDTHS["crown"]), fork_dress))

    # -- shock --
    shock_dress = _dress(bool(pick("rear_shock")), "#B9C2B8")
    parts.append(_polygon(tube(dt_mid, rock_b, *TUBE_WIDTHS["shock"]), shock_dress))
    can_cx, can_cy = P(dt_mid)
    parts.append(f'<circle cx="{can_cx}" cy="{can_cy}" r="{_r(46 * S)}" {_dress_attrs(shock_dress)}/>')

    # -- bars (cockpit) --
    bars_dress = _dress(bool(pick("cockpit")), "#22292A")
    parts.append(_polygon(tube(ht_top, stem_b, *TUBE_WIDTHS["bars"]), bars_dress))
    parts.append(_polygon(tube(stem_b, bar_pt, *TUBE_WIDTHS["stem"]), bars_dress))
    parts.append(_polygon(tube((bar_pt[0] + 4, bar_pt[1] + 2), (bar_pt[0] + 46, bar_pt[1] + 10), *TUBE_WIDTHS["grip"]), bars_dress))

    # -- saddle + post --
    saddle_dress = _dress(bool(pick("saddle_post")), "#22292A")
    parts.append(_polygon(tube(seat_top, (saddle_mm[0] + 6, saddle_mm[1] - 18), *TUBE_WIDTHS["post"]), saddle_dress))
    saddle_path = (
        f'M{_r(sad[0] - 40)},{_r(sad[1])} '
        f'C{_r(sad[0] - 30)},{_r(sad[1] - 9)} {_r(sad[0] + 16)},{_r(sad[1] - 10)} {_r(sad[0] + 40)},{_r(sad[1] - 3)} '
        f'L{_r(sad[0] + 36)},{_r(sad[1] + 5)} '
        f'C{_r(sad[0] + 8)},{_r(sad[1] + 10)} {_r(sad[0] - 26)},{_r(sad[1] + 9)} {_r(sad[0] - 40)},{_r(sad[1] + 4)} Z'
    )
    parts.append(f'<path d="{saddle_path}" {_dress_attrs(saddle_dress)}/>')

    # -- drive (ring, teeth, pulleys, cage, chain) --
    parts.append(f'<circle cx="{ring_x}" cy="{ring_y}" r="{ring_r}" {_dress_attrs(drive_dress)}/>')
    teeth = _ticks(ring_x, ring_y, ring_r, ring_r + 3.5, 32)
    for (x1, y1, x2, y2) in teeth:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{drive_dress["stroke"]}" opacity="{drive_dress["op"]}"/>')
    parts.append(f'<circle cx="{p1[0]}" cy="{p1[1]}" r="7" {_dress_attrs(drive_dress)}/>')
    parts.append(f'<circle cx="{p2[0]}" cy="{p2[1]}" r="7" {_dress_attrs(drive_dress)}/>')
    cage_pts = f'{p1[0] - 6},{p1[1]} {p2[0] - 6},{p2[1]} {p2[0] + 6},{p2[1]} {p1[0] + 6},{p1[1]}'
    parts.append(_polygon(cage_pts, drive_dress))
    chain1 = f'M{_r(ring_x)},{_r(ring_y - ring_r)} L{_r(rax + 4)},{_r(ray - 26)}'
    chain2 = f'M{_r(ring_x)},{_r(ring_y + ring_r)} L{p1[0]},{p1[1]} L{p2[0]},{p2[1]} L{_r(rax + 6)},{_r(ray + 16)}'
    for d in (chain1, chain2):
        parts.append(f'<path d="{d}" fill="none" stroke="{drive_dress["stroke"]}" opacity="{drive_dress["op"]}"/>')

    # -- pedals --
    pedals_dress = _dress(bool(pick("pedals")), "#2A3132")
    parts.append(_polygon(tube(bb, ped, *TUBE_WIDTHS["crank"]), pedals_dress))
    parts.append(_polygon(
        tube((ped[0] - ped_w / 2, ped[1] - 26), (ped[0] + ped_w / 2, ped[1] - 18), *TUBE_WIDTHS["pedal_plate"]),
        pedals_dress,
    ))

    # -- ebike motor --
    if motor_on:
        parts.append(_polygon(tube((bb[0] - 40, bb[1] + 30), (bb[0] + 60, bb[1] + 10), 190, 150), _dress(True, "#22292A")))

    # -- callouts: leader line + anchor dot per slot --
    bar_pt_px = P(bar_pt)
    ped_px = P(ped)
    anchors = {
        "frame": P(((seat_top[0] + ht_top[0]) / 2, (seat_top[1] + ht_top[1]) / 2)),
        "fork": P(f_at(0.55)),
        "rear_shock": P(((dt_mid[0] + rock_b[0]) / 2, (dt_mid[1] + rock_b[1]) / 2)),
        "wheelset": (fax, fay),
        "tires": (_r(fax + tireR * 0.72), _r(fay - tireR * 0.72)),
        "drivetrain": (_r(rax + 16), _r(ray - 18)),
        "brakes": (_r(fax - 26), _r(fay + 6)),
        "cockpit": (_r(bar_pt_px[0] + 24), _r(bar_pt_px[1] - 8)),
        "pedals": (_r(ped_px[0] + 6), _r(ped_px[1] + 8)),
        "saddle_post": (_r(sad[0] + 12), _r(sad[1] - 8)),
    }
    for slot in SLOTS:
        key = slot["key"]
        side = slot["side"]
        ty = slot["ty"]
        lx = 228 if side == "left" else 772
        ly = ty - 2
        ax, ay = anchors[key]
        picked = bool(pick(key))
        color = "#E0763F" if picked else "#5F6C62"
        parts.append(f'<line x1="{lx}" y1="{ly}" x2="{ax}" y2="{ay}" stroke="{color}" opacity="0.7"/>')
        parts.append(f'<circle cx="{lx}" cy="{ly}" r="2.6" fill="{color}"/>')
        parts.append(f'<circle cx="{ax}" cy="{ay}" r="5" fill="{color}"/>')

    body = "".join(parts)
    return f'<svg viewBox="0 0 1000 630" xmlns="http://www.w3.org/2000/svg">{body}</svg>'
