#!/usr/bin/env python3
"""ShipDeal dashboard — search bike parts that deliver to your region, cheapest first."""
from __future__ import annotations
import html
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from regions import REGIONS
from search import find_cheapest


def esc(s):
    return html.escape(str(s or ""))


def render(region="EU/UK", query="", brand="", budget=600, results=None, message=""):
    styles = "".join(f"<option {'selected' if r == region else ''}>{r}</option>"
                     for r in REGIONS)
    cards = []
    for r in (results or []):
        img = r.get("image")
        img_html = f"<img src='{esc(img)}' alt='{esc(r.get('brand'))}' loading='lazy'>" if img \
            else "<div class='noimg'>no image</div>"
        cards.append(
            f"<div class='opt'>"
            f"{img_html}"
            f"<div><b>{esc(r['brand'])}</b> — {esc(r['price'])} {esc(r['currency'])} "
            f"(~£{esc(r['price_gbp'])})<br>stock: {esc(r['stock'])} · {esc(r['ships'])}</div>"
            f"<a class='buy' href='{esc(r['url'])}' target='_blank'>Buy cheapest →</a>"
            f"</div>")
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<title>ShipDeal — cheapest parts that ship to you</title>
<style>
body{{font-family:system-ui;margin:0;padding:24px;background:#f4f5f7;color:#222}}
.wrap{{max-width:960px;margin:0 auto}}
h1{{font-size:1.6rem}} .card{{background:#fff;padding:18px;border-radius:12px;box-shadow:0 1px 3px #ccc}}
.row{{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:14px}}
select,input[[type=text]]{{padding:8px;border:1px solid #bbb;border-radius:8px}}
button{{padding:8px 18px;border:0;border-radius:8px;background:#1a6fb6;color:#fff;cursor:pointer}}
.opt{{border:1px solid #e0e0e0;border-radius:10px;padding:10px;margin:12px 0;display:flex;gap:10px;align-items:center}}
.opt img{{width:90px;height:90px;object-fit:contain}}
.opt .buy{{color:#fff;background:#18855f;padding:7px 14px;border-radius:8px;text-decoration:none}}
.noimg{{width:90px;height:90px;background:#eee;display:flex;align-items:center;justify-content:center;color:#999;font-size:11px}}
.msg{{margin-top:8px;color:#555}}
</style></head><body><div class='wrap'>
<h1>ShipDeal</h1><div class='card'>
<h3>Find the cheapest NEW {esc(query) or 'part'} that delivers to your region</h3>
<form method='post'>
<div class='row'>
<select name='region'>{styles}</select>
<input type='text' name='q' value='{esc(query)}' placeholder='part to search'>
<input type='text' name='brand' value='{esc(brand)}' placeholder='brand (optional)'>
<input type='number' name='budget' value='{budget}' title='budget in GBP'>
<button>Search</button></div></form>
<div class='msg'>{esc(message)}</div>
{''.join(cards)}
</div></div></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(render().encode())

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()
        q = parse_qs(body)
        region = (q.get("region") or ["EU/UK"])[0]
        query = (q.get("q") or [""])[0].strip()
        brand = (q.get("brand") or [""])[0].strip()
        try:
            budget = int((q.get("budget") or ["600"])[0])
        except ValueError:  # noqa: BLE001
            budget = 600
        message, results = "", []
        if query:
            try:
                results = find_cheapest(query, region, brand, budget)
                message = f"{len(results)} cheapest in-stock options found for {query} in {region}"
            except Exception as e:  # noqa: BLE001
                message = f"search failed: {e}"
        page = render(region, query, brand, budget, results, message)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode())


def main():
    port = 8018
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"ShipDeal live on http://localhost:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
