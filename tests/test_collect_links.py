"""RED: collect_links extracts product-page links per retailer (amazon /dp/, aliexpress /item/)."""
from populate import collect_links

md = ("[d](https://www.amazon.com/dp/B0BGRFBSZL?ref=x) "
      "[i](https://www.aliexpress.com/item/1005007401650661.html?browser_id=1) "
      "[t](https://www.probikesupply.com/products/maxxis-assegai-tire-29) "
      "[cdn](https://www.probikesupply.com/cdn/shop/products/x.jpg)")

amz = collect_links(md, "amazon")
axp = collect_links(md, "aliexpress")
pbs = collect_links(md, "probikesupply")

assert any("/dp/" in u for u in amz)
assert any("/item/" in u for u in axp)
assert any("/products/" in u for u in pbs)
# cdn/logo links are never treated as product pages
assert not any("/cdn/" in u for u in collect_links(md, "probikesupply"))
print("collect links OK")
