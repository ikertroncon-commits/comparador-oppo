# Guarda páginas de comprasmartphone para estudiar su estructura
import urllib.request, gzip
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36", "Accept-Language": "es-ES,es;q=0.9"}
for slug in ["samsung-galaxy-s26-ultra", "xiaomi-redmi-17"]:
    u = "https://comprasmartphone.com/telefonos/" + slug
    with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as r:
        open(f"herramientas/pagina-{slug}.html.gz", "wb").write(gzip.compress(r.read()))
u = "https://comprasmartphone.com/sitemap.xml"
try:
    with urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40) as r:
        open("herramientas/sitemap.xml.gz", "wb").write(gzip.compress(r.read()))
except Exception as e:
    open("herramientas/sitemap.err", "w").write(repr(e))
open("herramientas/resultado_prueba.json", "w").write('{"ok": true}')
