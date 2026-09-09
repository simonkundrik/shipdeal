#!/usr/bin/env python3
"""ShipDeal dashboard — catalogue search + filters + build cart, cheapest sellers first."""
from __future__ import annotations
import html
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from builds import Pick, add, load, save, total
from catalogue import COMPONENTS, brand_search, style_defaults
from filters import Filters, apply
from populate import cheapest_by_component, load_products
from countries import (  # noqa: E402
    COUNTRY_INFO, REGION_ALIAS, country_info, groups, money, tax_line,
)
from landed import landed_row, sort_by_landed
from regions import REGIONS, RETAILERS, retailers_for, shipping_hint
from stock_checker import check_stock, passes_stock
from search import find_cheapest


def esc(s):
    return html.escape(str(s or ""))


def parse_filters(form: dict) -> Filters:
    """Parse a form into Filters. Accepts both parse_qs list-values and plain scalar dicts."""
    def _val(key, default):
        v = form.get(key)
        if isinstance(v, list):
            return v[0] if v else default
        return v if v is not None else default

    def _num(key, default):
        raw = _val(key, None)
        try:
            return int(raw)
        except (ValueError, TypeError):  # noqa: BLE001
            return default
    return Filters(
        style=_val("style", "enduro"),
        wheel=_val("wheel", ""),
        travel_min=_num("travel", 0),
        brand=_val("brand", "").strip(),
        price_min=_num("min", 0),
        price_max=_num("max", 99999),
        stock=_val("stock", ""),
        component=_val("component", ""),
    )


FONT_LINK = ("<link href='https://fonts.googleapis.com/css2?"
             "family=Big+Shoulders+Display:wght@800&family=Newsreader:ital,wght@0,400;0,500"
             "&family=Barlow+Condensed:wght@700&family=DM+Mono:wght@500' rel='stylesheet'>")

# Trailhead design system (design/DESIGN.md in the handoff bundle): bone paper canvas, pine ink,
# clay accent, pill controls, rounded shadowed cards, NO 1px outlines anywhere.
STYLE = """
:root{--paper:#F2EDE3;--paper2:#EBE4D8;--card:#FBF8F2;--sunken:#EFE8DB;--input:#F1EADD;
--dust:#D5CBB8;--ink:#16211C;--ink2:#2C3830;--ink60:#4E5A52;--ink40:#8A8578;
--clay:#B94A26;--clay-light:#E0763F;--clay-pale:#E8B39C;--moss:#3E6B44;--mossT:#2C5333;
--amber:#9A6A12;--amberT:#6F4C0D;--err:#D9634A;--warn:#D8A23C;--ok:#6FBE7E}
body{font-family:'Newsreader',Georgia,serif;background:var(--paper);color:var(--ink);margin:0}
.wrap{max-width:1320px;margin:0 auto;padding:24px}
h1{font-family:'Big Shoulders Display',sans-serif;font-weight:800;text-transform:uppercase;letter-spacing:-.02em;line-height:.88;color:var(--ink)}
.sticky{position:sticky;top:0;z-index:40;display:flex;align-items:center;gap:22px;flex-wrap:wrap;padding:14px 32px;background:rgba(242,237,227,.92);backdrop-filter:blur(14px)}
select,input{background:var(--input);border:0;border-radius:999px;padding:8px 14px;min-height:44px;font-family:'Barlow Condensed',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:.08em}
button,.pill{background:var(--sunken);border:0;border-radius:999px;padding:8px 18px;font-family:'Barlow Condensed',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--ink);cursor:pointer;min-height:44px}
button:hover{background:var(--ink);color:var(--paper)}
.card,.opt{background:var(--card);border:0;border-radius:26px;padding:22px 28px;box-shadow:0 18px 40px -30px rgba(22,33,28,.45)}
.row{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:14px}
.hero{height:clamp(460px,72vh,660px);border-radius:0 0 34px 34px;background:linear-gradient(to top,rgba(22,33,28,.9) 0%,rgba(22,33,28,.45) 45%,rgba(22,33,28,.15) 100%);color:var(--paper);display:flex;align-items:flex-end;padding:40px}
.gate{background:var(--paper2);display:flex;flex-wrap:wrap;gap:10px;padding:18px;border-radius:18px}
.badge{background:var(--card);border:0;border-radius:18px;padding:14px;flex:1 1 220px}
.badge b{font-family:'Big Shoulders Display',sans-serif;font-size:1.4rem;color:var(--clay)}
.badge span{font-family:'Barlow Condensed',sans-serif;font-weight:700;text-transform:uppercase;letter-spacing:.12em}
.badge small{color:var(--ink60);display:block;margin-top:4px}
.banner{background:var(--ink);color:var(--paper);font-family:'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.12em;padding:14px 18px;border-radius:999px}
.trail{background:#cdd3cb;border-radius:18px;height:260px;display:flex;align-items:center;justify-content:center;color:var(--ink60);font-family:'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.12em;margin:14px 0}
.tagline{font-family:'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.12em;color:var(--ink60);margin:4px 0 14px}
.proof{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}
.opt img{width:196px;height:150px;object-fit:contain;background:var(--sunken);border-radius:18px}
.noimg{width:196px;height:150px;background:var(--sunken);display:flex;align-items:center;justify-content:center;color:var(--ink40);font-size:11px;border-radius:18px}
.price{font-family:'DM Mono',monospace;font-weight:500}
.landed{font-family:'DM Mono',monospace;font-weight:500;font-size:30px}
.breakdown{font-family:'DM Mono',monospace;font-size:11.5px;color:var(--ink60)}
.mid{flex:1;min-width:0}
.kicker{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:13px;text-transform:uppercase;letter-spacing:.16em;color:var(--clay)}
.brand{font-family:'Big Shoulders Display',sans-serif;font-weight:800;font-size:27px;text-transform:uppercase}
.listed,.dl,.listed-at{font-family:'DM Mono',monospace;font-size:12px;color:var(--ink60)}
.rail{text-align:right;min-width:220px}
.buy{background:var(--clay);color:var(--paper);border-radius:999px;padding:14px 20px;text-decoration:none;font-family:'Big Shoulders Display',sans-serif;font-weight:800;font-size:17px;text-transform:uppercase;display:inline-block}
.buy:hover{background:var(--ink)}
.stock-in{background:rgba(62,107,68,.15);color:var(--mossT);border-radius:999px;padding:4px 12px;font-family:'Barlow Condensed',sans-serif;font-weight:700;text-transform:uppercase}
.stock-unknown{background:rgba(154,106,18,.17);color:var(--amberT);border-radius:999px;padding:4px 12px;font-family:'Barlow Condensed',sans-serif;font-weight:700;text-transform:uppercase}
.build{background:var(--ink);color:var(--paper);border-radius:28px;padding:18px;box-shadow:0 28px 60px -36px rgba(22,33,28,.65)}
.kit{background:var(--ink);color:var(--paper);border-radius:28px;padding:18px;position:sticky;top:92px;box-shadow:0 28px 60px -36px rgba(22,33,28,.65)}
.ring{font-family:'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.12em;color:var(--ink60)}
.footer{background:var(--paper2);border-radius:18px;padding:18px;margin-top:18px;font-family:'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.12em}
.message{margin:8px 0;color:var(--ink60)}
.note-dm{background:var(--paper2);border-radius:999px;padding:8px 18px;font-family:'DM Mono',monospace;font-size:12.5px;color:#6B5A50;margin:14px 0}
"""



def render(country="GB", query="", brand="", budget=600, results=None, message="", filters=None):
    f = filters or Filters()
    country_opts = "".join(
        "<optgroup label='{}'>".format(esc(g[0])) +
        "".join("<option {} value='{}'>{}</option>".format(
            "selected" if cc == country else "", cc, esc(name)) for cc, name in g[1]) +
        "</optgroup>" for g in groups())
    comps = "".join(f"<option {'selected' if f.component == c else ''}>{c}</option>"
                    for c in COMPONENTS)
    cards = []
    for r in (results or []):
        if not apply(r, f):
            continue
        img = r.get("image")
        img_html = (f"<img src='{esc(img)}' alt='{esc(r.get('brand'))}' loading='lazy'>" if img
                    else "<div class='noimg'>no image</div>")
        component = r.get("component") or f.component or ""
        cards.append(
            f"<div class='opt'>{img_html}"
            f"<div><b>{esc(r['brand'])}</b> — {esc(r['price'])} {esc(r['currency'])} "
            f"(~£{esc(r['price_gbp'])})<br>"
            f"stock: {esc(r.get('stock'))} ({esc(r.get('stock_evidence')) or '—'})<br>"
            f"wheel: {esc(r.get('wheel') or '—')} · travel: {esc(r.get('travel') or '—')}<br>"
            f"{esc(r.get('ships'))}</div>"
            f"<a class='buy' href='{esc(r['url'])}' target='_blank'>Buy cheapest →</a>"
            f"<button onclick='addToBuild(\"{esc(r['component'] or component)}\","
            f"\"{esc(r['url'])}\",\"{esc(r['brand'])}\",\"{esc(r['price'])}\","
            f"\"{esc(r['currency'])}\",{esc(r['price_gbp'])},\"{esc(r.get('image') or '')}\","
            f"\"{esc(r.get('ships') or '')}\")'>Add to build</button>"
            f"</div>")
    picks = json.loads(load())
    my_items = "".join(
        f"<li>{esc(p['brand'])} — {esc(p['price'])} {esc(p['currency'])} (~£{esc(p['price_gbp'])}) "
        f"<a href='{esc(p['url'])}'>buy</a> "
        f"<button onclick='rmFromBuild(\"{esc(p['component'])}\")'>remove</button></li>"
        for p in picks.values())
    my_total = total(picks)
    proof = """<div class='proof'>
  <div class='badge'><b>01</b><span>NEW ONLY</span><small>Used and second-hand listings are rejected on the title.</small></div>
  <div class='badge'><b>02</b><span>STOCK, WITH EVIDENCE</span><small>We quote the phrase that proved it — &ldquo;add to cart&rdquo;, &ldquo;in stock&rdquo;.</small></div>
  <div class='badge'><b>03</b><span>THE REAL PRICE</span><small>Authoritative modal price. Fees and financing lines thrown out.</small></div>
  <div class='badge'><b>04</b><span>A LINK THAT LOADS</span><small>Direct product page, checked live. No homepage redirects.</small></div>
</div>"""
    retail_ring = " · ".join(k for k in RETAILERS if RETAILERS[k].get("scrapable"))
    landed_note = (f"Every price here is the landed cost for {esc(country)} — the listing with its "
                   f"origin VAT stripped, plus that retailer&rsquo;s shipping to your door, plus the "
                   f"duty, {esc(country)} tax rate and clearance fee you&rsquo;ll actually be billed. "
                   f"A German listing is not a Swedish price. Confirm at checkout before you order.")
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<title>ShipDeal — search</title>
{FONT_LINK}<style>{STYLE}</style></head><body><div class='wrap'>
<div class='banner'>NEW · IN STOCK · LANDED PRICE FOR {esc(country.upper())}</div>
<div class='trail'>Drop a full-bleed trail shot — rider, dust, treeline</div>
<h1>THE TRAILHEAD</h1>
<p class='tagline'>Pick your country, pick a part, one search.</p>
<div class='card'><h3>Find the cheapest {esc(f.component or 'part')} — NEW, in stock, at your landed price</h3>
<form method='post'>
<div class='row'>
<select name='country'>{country_opts}</select>
<select name='component'>{comps}</select>
<input type='text' name='q' value='{esc(query)}' placeholder='part to search'>
<input type='text' name='brand' value='{esc(brand)}' placeholder='brand'>
<select name='style'><option {'selected' if f.style=='xc' else ''}>xc</option><option {'selected' if f.style=='enduro' else ''}>enduro</option><option {'selected' if f.style=='freeride' else ''}>freeride</option><option {'selected' if f.style=='downhill' else ''}>downhill</option><option {'selected' if f.style=='ebike' else ''}>ebike</option></select>
<select name='wheel'><option value=''>any wheel</option><option {'selected' if f.wheel=='29' else ''} value='29'>29</option><option {'selected' if f.wheel=='27.5' else ''} value='27.5'>27.5</option></select>
<input type='number' name='travel' value='{f.travel_min}' title='min fork travel mm'>
<input type='number' name='min' value='{f.price_min}' title='min £'>
<input type='number' name='max' value='{f.price_max if f.price_max!=99999 else ''}' title='max £'>
<select name='stock'><option value=''>any stock</option><option {'selected' if f.stock=='in_stock' else ''} value='in_stock'>in stock</option></select>
<button>Search</button></div></form>
<div class='message'>{esc(message)}</div>
<div class='message'>Choose a part, press <i>Add to build</i>, open <i>Buy cheapest</i> to order,
and track your assembled bike in <i>My Build</i>.</div>
</div>
{proof}
<div class='ring'><b>RETAILER RING · LIVE SCRAPE</b><br>{esc(retail_ring)}</div>
<div class='card'><h3>CHEAPEST FIRST — sorted on landed cost to {esc(country)}</h3>
<div class='note-dm'>{esc(landed_note)}</div></div>
<div class='build'><h3>My Build</h3><ul>{my_items}</ul><b>Total: £{my_total}</b></div>
{''.join(cards)}
<div class='footer'>SHIPDEAL · NO USED · NO DEAD LINKS · NO GENERIC SEARCH JUNK</div>
</div>
<script>
function addToBuild(component,url,brand,price,currency,gbp,image,ships,retailer,wheel,travel,stock){{
  fetch('/build/add',{{method:'POST',body:new URLSearchParams({{component,url,brand,price,currency,gbp,String(image),String(ships)||'',String(retailer)||'',String(wheel)||'',String(travel)||'0',String(stock)||''}})}})
    .then(()=>location.reload());}}
function rmFromBuild(component){{
  fetch('/build/remove',{{method:'POST',body:new URLSearchParams({{component}})}})
    .then(()=>location.reload());}}
</script>
</body></html>"""


def row_line(row, country="GB"):
    """Trailhead result card: landed label, breakdown, delivery line, stock badge, buy pill."""
    img = row.get("image")
    img_html = (f"<img src='{esc(img)}' alt='{esc(row.get('brand'))}' loading='lazy'>" if img
                else "<div class='noimg'>no image</div>")
    L = row.get("landed") or {}
    comp = row.get("component") or ""
    brand = row.get("brand") or ""
    retailer = esc(row.get("retailer") or "")
    listed = f"{esc(row.get('price'))} {esc(row.get('currency'))} (~£{esc(row.get('price_gbp'))})"
    landed_label = esc(L.get("label") or "")
    breakdown = esc(L.get("breakdown") or "")
    duty_note = esc(L.get("duty_note") or "")
    days = L.get("days")
    origin = esc(L.get("origin") or "")
    stock = row.get("stock") or "unknown"
    ev = esc(row.get("stock_evidence") or "")
    stock_cls = "stock-in" if stock == "in_stock" else "stock-unknown"
    dl = f"delivered to {esc(country)} in ~{days} days · {duty_note}" if days else \
        f"delivered to {esc(country)} · {duty_note}"
    total_for_cart = L.get("total_gbp") if L.get("total_gbp") is not None else row.get("price_gbp")
    return (f"<div class='opt'>{img_html}"
            f"<div class='mid'><div class='kicker'>{esc(comp)} · {retailer}</div>"
            f"<div class='brand'>{esc(brand)}</div>"
            f"<div class='listed'>{listed}</div>"
            f"<span class='{stock_cls}'>{esc(stock)} ({ev})</span>"
            f"<div class='dl'>{dl}</div></div>"
            f"<div class='rail'><div class='landed'>{landed_label}</div>"
            f"<div class='breakdown'>{breakdown}</div>"
            f"<div class='listed-at'>listed {esc(row.get('price'))} {esc(row.get('currency'))} at "
            f"{retailer} ({origin})</div></div>"
            f"<a class='buy' href='{esc(row.get('url'))}' target='_blank'>BUY CHEAPEST →</a>"
            f"<button onclick='addToBuild(\\\"{esc(comp)}\\\",\\\"{esc(row.get('url'))}\\\","
            f"\\\"{esc(brand)}\\\",\\\"{esc(row.get('price'))}\\\",\\\"{esc(row.get('currency'))}\\\","
            f"{total_for_cart},\\\"{esc(row.get('image') or '')}\\\",\\\"{esc(row.get('ships_hint') or '')}\\\","
            f"\\\"{esc(row.get('retailer') or '')}\\\",\\\"{esc(row.get('wheel') or '')}\\\","
            f"\\\"{esc(row.get('travel') or 0)}\\\",\\\"{esc(row.get('stock') or '')}\\\")'>"
            f"Add to build</button></div>")


def browse_render(components, country="GB", rows=None):
    """Browse catalogue sorted on landed cost; retailers not delivering are dropped and counted."""
    if rows is None:
        rows = []
        for c in components:
            rows.extend(cheapest_by_component(c, country))
    priced, hidden = sort_by_landed(rows, country)
    cards = "".join(row_line(r, country) for r in priced)
    picks = json.loads(load())
    my_items = "".join(
        f"<li>{esc(p['brand'])} — {esc(p['price'])} {esc(p['currency'])} (~£{esc(p['price_gbp'])})"
        + (f" · +£{esc(p.get('total_gbp'))} incl delivery" if p.get("total_gbp") is not None else "")
        + f"<a href='{esc(p['url'])}'>buy</a>"
        f"<button onclick='rmFromBuild(\"{esc(p['component'])}\")'>remove</button></li>"
        for p in picks.values())
    my_total = total(picks)
    cname = ", ".join(components)
    country_opts = "".join(
        "<optgroup label='{}'>".format(esc(g[0])) +
        "".join("<option {} value='{}'>{}</option>".format(
            "selected" if cc == country else "", cc, esc(name)) for cc, name in g[1]) +
        "</optgroup>" for g in groups())
    hidden_note = (f"<div class='note-dm'>{hidden} retailer(s) do not deliver to {esc(country)} "
                   f"and were not priced</div>" if hidden else "")
    info = country_info(country)
    tax = tax_line(country)
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<title>ShipDeal — Browse catalogue</title>
{FONT_LINK}<style>{STYLE}</style></head><body>
<div class='sticky'>
<span style="font-family:'Big Shoulders Display',sans-serif;font-weight:800;font-size:26px;letter-spacing:-.02em;text-transform:uppercase">SHIPDEAL</span>
<span style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--clay)">Trail-tested parts index</span>
<div style="flex:1"></div>
<div style="text-align:right"><span style="font-family:'DM Mono',monospace;font-size:11px;color:var(--ink60)">{esc(tax)}</span>
<form method='get'><select name='country'>{country_opts}<button>Switch country</button></form></div>
<div class='build'>BUILD · £{my_total}</div>
</div>
<div class='wrap'>
<div class='hero'><div><div style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:13px;letter-spacing:.24em;text-transform:uppercase;color:var(--clay-pale)">New · in stock · landed price for {esc(country)}</div>
<h1 style="font-family:'Big Shoulders Display',sans-serif;font-weight:800;font-size:clamp(52px,9vw,132px);line-height:.88;letter-spacing:-.025em;text-transform:uppercase;color:#F2EDE3">Parts that make it to the trailhead</h1></div></div>
<div class='gate'>
<div class='badge'><b>01</b><span>New only</span><small>Used and second-hand listings are rejected on the title.</small></div>
<div class='badge'><b>02</b><span>Stock, with evidence</span><small>We quote the phrase that proved it — &ldquo;add to cart&rdquo;, &ldquo;in stock&rdquo;.</small></div>
<div class='badge'><b>03</b><span>The real price</span><small>Authoritative modal price. Fees and financing lines thrown out.</small></div>
<div class='badge'><b>04</b><span>A link that loads</span><small>Direct product page, checked live. No homepage redirects.</small></div>
</div>
<div class='card'><h3>CHEAPEST FIRST — sorted on the landed cost to {esc(country)}</h3>
<div class='note-dm'>{esc(info['name'])} · landed price = net + ship + duty + VAT + clearance; same listing priced to DE differs from SE.</div>
</div>
{hidden_note}
<div class='kit'><h3>My Build</h3><ul>{my_items}</ul><b>Landed in {esc(country)}: £{my_total}</b></div>
{cards}
<div class='footer'>SHIPDEAL · NO USED · NO DEAD LINKS · NO GENERIC SEARCH JUNK</div>
</div>
<script>
function addToBuild(component,url,brand,price,currency,gbp,image,ships,retailer,wheel,travel,stock){{
  fetch('/build/add',{{method:'POST',body:new URLSearchParams({{component,url,brand,price,currency,gbp,String(image),String(ships)||'',String(retailer)||'',String(wheel)||'',String(travel)||'0',String(stock)||''}})}})
    .then(()=>location.reload());}}
function rmFromBuild(component){{
  fetch('/build/remove',{{method:'POST',body:new URLSearchParams({{component}})}})
    .then(()=>location.reload());}}
</script>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, ctype):
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        qs = parse_qs(urlparse(self.path).query)
        if "browse" in qs:
            comps = qs.get("component") or list(COMPONENTS.keys())
            if not isinstance(comps, list):
                comps = [comps]
            country = (qs.get("country") or ["GB"])[0]
            self._send(browse_render(comps, country), "text/html; charset=utf-8")
        else:
            self._send(render(), "text/html; charset=utf-8")

    def do_POST(self):  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        form = parse_qs(body)
        if path == "/build/add":
            p = Pick(component=(form["component"][0] if "component" in form else ""),
                     url=(form["url"][0] if "url" in form else ""),
                     brand=(form["brand"][0] if "brand" in form else ""),
                     price=(form["price"][0] if "price" in form else ""),
                     currency=(form["currency"][0] if "currency" in form else "GBP"),
                     price_gbp=float(form["gbp"][0]) if "gbp" in form else 0.0,
                     image=(form["image"][0] if "image" in form else ""),
                     ships=(form["ships"][0] if "ships" in form else ""),
                     retailer=(form["retailer"][0] if "retailer" in form else ""),
                     wheel=(form["wheel"][0] if "wheel" in form else ""),
                     travel=int(float(form["travel"][0])) if "travel" in form and form["travel"][0] else 0,
                     stock=(form["stock"][0] if "stock" in form else ""),
                     total_gbp=float(form["gbp"][0]) if "gbp" in form else None)
            picks = json.loads(load())
            save(add(picks, p))
            self._send("ok", "text/plain")
            return
        if path == "/build/remove":
            comp = form["component"][0] if "component" in form else ""
            picks = json.loads(load())
            picks.pop(comp, None)
            save(picks)
            self._send("ok", "text/plain")
            return
        country = (form.get("country") or ["GB"])[0]
        query = (form.get("q") or [""])[0].strip()
        brand = (form.get("brand") or [""])[0].strip()
        f = parse_filters(form)
        comp = f.component
        if comp and not query:
            query = brand_search(comp, f.brand or "") if f.brand else comp
        try:
            budget = int((form.get("budget") or ["600"])[0])
        except (ValueError, TypeError):  # noqa: BLE001
            budget = 600
        message, results = "", []
        if query:
            message = f"searching {query} for {country} (filters: {f.style})"
            raw = find_cheapest(query, country, brand, budget)
            results = []
            for o in raw:
                sd, ev = check_stock(o.get("stock", "unknown"), o.get("component") or comp)
                o["component"] = comp
                o["stock"] = sd
                o["stock_evidence"] = ev
                if passes_stock(sd, comp) and apply(o, f):
                    results.append(o)
            message = f"{len(results)} in-stock options for {query} in {country}"
        self._send(render(country, query, brand, budget, results, message, f),
                   "text/html; charset=utf-8")


def main():
    port = 8018
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"ShipDeal live on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
