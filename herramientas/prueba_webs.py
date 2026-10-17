# Prueba: ¿se pueden leer los precios de El Corte Inglés desde comprasmartphone.com?
import json, re, urllib.request
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept-Language": "es-ES,es;q=0.9"}
out = {}
for slug in ["samsung-galaxy-s26-ultra", "oppo-find-x9-pro", "xiaomi-redmi-note-17-pro"]:
    u = "https://comprasmartphone.com/telefonos/" + slug
    r = {"url": u}
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as resp:
            body = resp.read().decode("utf-8", "replace"); r["status"] = resp.status; r["len"] = len(body)
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', body, re.S)
        r["next_data"] = bool(m)
        i = body.find("Corte Ingl")
        r["eci_ctx"] = [body[max(0, j-400):j+400] for j in [m2.start() for m2 in re.finditer("Corte Ingl", body)][:4]]
        if m:
            nd = m.group(1); r["nd_len"] = len(nd)
            k = nd.find("Corte Ingl"); r["nd_eci"] = nd[max(0, k-1500):k+800] if k >= 0 else None
        # rutas de datos de Next
        r["build"] = re.findall(r'"buildId":"([^"]+)"', body)[:1]
        r["apis"] = list(set(re.findall(r'(/api/[A-Za-z0-9_/\-]+)', body)))[:20]
    except Exception as e:
        r["error"] = repr(e)[:300]
    out[slug] = r
json.dump(out, open("herramientas/resultado_prueba.json", "w"), ensure_ascii=False, indent=1)
print({k: (v.get("status"), v.get("len"), v.get("next_data"), v.get("error")) for k, v in out.items()})
