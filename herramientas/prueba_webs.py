# Prueba: ¿se puede leer el precio de cada tienda desde un servidor?
import json, re, sys, urllib.request
URLS = {
 "mm_peninsula": "https://www.mediamarkt.es/es/product/_movil-samsung-galaxy-s26-ultra-negro-512-gb-12-gb-ram-69-qhd-qualcomm-snapdragon-8-elite-gen-5-5000-mah-android-16-1620281.html",
 "mm_canarias_home": "https://canarias.mediamarkt.es/collections/smartphones/products.json?limit=5",
 "mm_canarias_search": "https://canarias.mediamarkt.es/search/suggest.json?q=galaxy%20s26%20ultra&resources[type]=product",
 "worten_canarias": "https://canarias.worten.es/productos/smartphone-samsung-galaxy-s26-ultra-6-9-12-gb-512-gb-blanco-8759628",
 "worten_peninsula": "https://www.worten.es/productos/smartphone-samsung-galaxy-s26-ultra-6-9-12-gb-256-gb-azul-claro-8759622",
 "eci_peninsula": "https://www.elcorteingles.es/electronica/A56390869-8806097640233-pr-movil-samsung-galaxy-a17-5g-67-exynos-1330-azul-256-gb-8-gb-ram/",
 "eci_canarias": "https://www.elcorteingles.es/canarias/electronica/A56390869-8806097640233-pr-movil-samsung-galaxy-a17-5g-67-exynos-1330-azul-256-gb-8-gb-ram/",
 "eci_api": "https://www.elcorteingles.es/api/product/A56390869?product_id=A56390869",
}
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
     "Accept-Language": "es-ES,es;q=0.9", "Accept": "text/html,application/json;q=0.9,*/*;q=0.8"}
out = {}
for k, u in URLS.items():
    r = {"url": u}
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=30) as resp:
            body = resp.read().decode("utf-8", "replace"); r["status"] = resp.status; r["len"] = len(body)
            r["ld_price"] = re.findall(r'"price"\s*:\s*"?([\d.,]+)', body)[:6]
            r["meta_price"] = re.findall(r'(?:itemprop|property)="(?:product:)?price(?::amount)?"\s+content="([\d.,]+)"', body)[:4]
            r["euros"] = re.findall(r'(\d{2,4}(?:[.,]\d{2})?)\s?(?:€|&euro;)', body)[:12]
            r["muestra"] = body[:300] if len(body) < 2000 else ""
    except Exception as e:
        r["error"] = repr(e)[:300]
    out[k] = r
json.dump(out, open("herramientas/resultado_prueba.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
