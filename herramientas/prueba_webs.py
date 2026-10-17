# Descarga el catálogo de móviles de MediaMarkt Canarias (Shopify) para emparejar modelos
import json, urllib.request
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
out = {}
for col in ["smartphones", "telefonia", "moviles", "all"]:
    items = []
    for page in range(1, 15):
        u = f"https://canarias.mediamarkt.es/collections/{col}/products.json?limit=250&page={page}"
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as r:
                d = json.loads(r.read().decode("utf-8"))
        except Exception as e:
            items.append({"error": repr(e)[:200], "page": page}); break
        ps = d.get("products", [])
        if not ps: break
        for p in ps:
            items.append({"t": p.get("title"), "h": p.get("handle"), "v": p.get("vendor"), "type": p.get("product_type"),
                          "var": [{"p": x.get("price"), "c": x.get("compare_at_price"), "a": x.get("available"), "t": x.get("title")} for x in p.get("variants", [])]})
        if len(ps) < 250: break
    out[col] = items
json.dump(out, open("herramientas/resultado_prueba.json", "w"), ensure_ascii=False, indent=0)
print({k: len(v) for k, v in out.items()})
