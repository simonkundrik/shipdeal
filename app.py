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


def render(region="EU/UK", query="", brand="", budget=600, results=None, message="", filters=None):
    f = filters or Filters()
    styles = "".join(f"<option {'selected' if r == region else ''}>{r}</option>" for r in REGIONS)
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
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<title>ShipDeal — cheapest factory parts, in stock, shipped to you</title>
<style>
body{{font-family:system-ui;margin:0;padding:24px;background:#f4f5f7;color:#222}}
.wrap{{max-width:980px;margin:0 auto}} h1{{font-size:1.6rem}}
.card{{background:#fff;padding:18px;border-radius:12px;box-shadow:0 1px 3px #ccc}}
.row{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0}}
select,input{{padding:8px;border:1px solid #bbb;border-radius:8px}}
button{{padding:8px 14px;border:0;border-radius:8px;background:#1a6fb6;color:#fff;cursor:pointer}}
.opt{{border:1px solid #e0e0e0;border-radius:10px;padding:10px;margin:12px 0;display:flex;gap:10px;align-items:center}}
.opt img{{width:90px;height:90px;object-fit:contain}}
.opt .buy{{color:#fff;background:#18855f;padding:7px 14px;border-radius:8px;text-decoration:none}}
.noimg{{width:90px;height:90px;background:#eee;display:flex;align-items:center;justify-content:center;color:#999;font-size:11px}}
.build{{background:#eaf3ff;border:1px solid #9cc3e3;border-radius:10px;padding:12px;margin:12px 0}}
.message{{margin:8px 0;color:#555}}
</style></head><body><div class='wrap'>
<h1>ShipDeal</h1>
<div class='card'><h3>Find the cheapest {esc(f.component or 'part')} that is NEW, in stock, shipped to your region</h3>
<form method='post'>
<div class='row'>
<select name='region'>{styles}</select>
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
<div class='build'><h3>My Build</h3><ul>{my_items}</ul><b>Total: £{my_total}</b></div>
{''.join(cards)}
</div>
<script>
function addToBuild(component,url,brand,price,currency,gbp,image,ships){{
  fetch('/build/add',{{method:'POST',body:new URLSearchParams({{component,url,brand,price,currency,gbp,String(image),ships}})}})
    .then(()=>location.reload());}}
function rmFromBuild(component){{
  fetch('/build/remove',{{method:'POST',body:new URLSearchParams({{component}})}})
    .then(()=>location.reload());}}
</script>
</body></html>"""


def row_line(row):
    """HTML card showing exact price + delivery -> total (delivery-unknown flagged)."""
    img = row.get("image")
    img_html = (f"<img src='{esc(img)}' alt='{esc(row.get('brand'))}' loading='lazy'>" if img
                else "<div class='noimg'>no image</div>")
    price_gbp = row.get("price_gbp")
    ship = row.get("shipping_gbp")
    total_gbp = row.get("total_gbp")
    price_txt = f"{esc(row.get('price'))} {esc(row.get('currency'))} (~£{price_gbp})"
    ship_txt = "delivery unknown" if ship is None else f"+ £{ship} delivery"
    total_txt = f"= £{total_gbp}" if total_gbp is not None else "(total incl delivery unknown)"
    total_for_cart = total_gbp if total_gbp is not None else price_gbp
    return (f"<div class='opt'>{img_html}"
            f"<div><b>{esc(row.get('brand'))}</b> — {price_txt}<br>{ship_txt} {total_txt}<br>"
            f"stock: {esc(row.get('stock'))} ({esc(row.get('stock_evidence')) or '—'}) · "
            f"retailer: {esc(row.get('retailer'))}<br>{esc(row.get('ships_hint') or '')}</div>"
            f"<a class='buy' href='{esc(row.get('url'))}' target='_blank'>Buy cheapest →</a>"
            f"<button onclick='addToBuild(\"{esc(row.get('component'))}\",\"{esc(row.get('url'))}\","
            f"\"{esc(row.get('brand'))}\",\"{esc(row.get('price'))}\",\"{esc(row.get('currency'))}\","
            f"{total_for_cart},\"{esc(row.get('image') or '')}\",\"{esc(row.get('ships_hint') or '')}\")'>"
            f"Add to build</button></div>")


def browse_render(components, region="EU/UK", rows=None):
    """Browse catalogue from the product DB, cheapest retailer incl delivery."""
    if rows is None:
        rows = []
        for c in components:
            rows.extend(cheapest_by_component(c, region))
        rows.sort(key=lambda r: (r.get("total_gbp") if r.get("total_gbp") is not None else 1e9))
    cards = "".join(row_line(r) for r in rows)
    picks = json.loads(load())
    my_items = "".join(
        f"<li>{esc(p['brand'])} — {esc(p['price'])} {esc(p['currency'])} (~£{esc(p['price_gbp'])})"
        + (f" · +£{esc(p.get('total_gbp'))} incl delivery" if p.get("total_gbp") is not None else "")
        + f"<a href='{esc(p['url'])}'>buy</a>"
        f"<button onclick='rmFromBuild(\"{esc(p['component'])}\")'>remove</button></li>"
        for p in picks.values())
    my_total = total(picks)
    cname = ", ".join(components)
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<title>ShipDeal — browse catalogue</title>
<style>
body{{font-family:system-ui;margin:0;padding:24px;background:#f4f5f7;color:#222}}
.wrap{{max-width:980px;margin:0 auto}} h1{{font-size:1.6rem}}
.card{{background:#fff;padding:18px;border-radius:12px;box-shadow:0 1px 3px #ccc}}
.opt{{border:1px solid #e0e0e0;border-radius:10px;padding:10px;margin:12px 0;display:flex;gap:10px;align-items:center}}
.opt img{{width:90px;height:90px;object-fit:contain}}
.opt .buy{{color:#fff;background:#18855f;padding:7px 14px;border-radius:8px;text-decoration:none}}
.noimg{{width:90px;height:90px;background:#eee;display:flex;align-items:center;justify-content:center;color:#999;font-size:11px}}
button{{padding:8px 14px;border:0;border-radius:8px;background:#1a6fb6;color:#fff;cursor:pointer}}
.build{{background:#eaf3ff;border:1px solid #9cc3e3;border-radius:10px;padding:12px;margin:12px 0}}
</style></head><body><div class='wrap'>
<h1>ShipDeal — Browse catalogue ({esc(region)})</h1>
<div class='card'><h3>{esc(cname)} — cheapest retailer incl delivery</h3></div>
<div class='build'><h3>My Build</h3><ul>{my_items}</ul><b>Total: £{my_total} (incl delivery)</b></div>
{cards}
<a href='/'>Back to search</a>
<script>
function addToBuild(component,url,brand,price,currency,gbp,image,ships){{
  fetch('/build/add',{{method:'POST',body:new URLSearchParams({{component,url,brand,price,currency,gbp,String(image),ships}})}})
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
            region = (qs.get("region") or ["EU/UK"])[0]
            self._send(browse_render(comps, region), "text/html; charset=utf-8")
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
        region = (form.get("region") or ["EU/UK"])[0]
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
            message = f"searching {query} for {region} (filters: {f.style})"
            raw = find_cheapest(query, region, brand, budget)
            results = []
            for o in raw:
                sd, ev = check_stock(o.get("stock", "unknown"), o.get("component") or comp)
                o["component"] = comp
                o["stock"] = sd
                o["stock_evidence"] = ev
                if passes_stock(sd, comp) and apply(o, f):
                    results.append(o)
            message = f"{len(results)} in-stock options for {query} in {region}"
        self._send(render(region, query, brand, budget, results, message, f),
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
