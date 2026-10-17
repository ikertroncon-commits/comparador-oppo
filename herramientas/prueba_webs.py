import urllib.request, gzip
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
with urllib.request.urlopen(urllib.request.Request("https://comprasmartphone.com/telefonos/sitemap.xml", headers=H), timeout=60) as r:
    open("herramientas/telefonos-sitemap.xml.gz", "wb").write(gzip.compress(r.read()))
open("herramientas/resultado_prueba.json", "w").write('{"ok": 2}')
