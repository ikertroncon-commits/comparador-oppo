"""Precios de El Corte Inglés (Península) -> precios/eci_pen.json

La web de El Corte Inglés no deja leer sus precios a un programa, pero el comparador
comprasmartphone.com los recoge a diario (con el enlace a la ficha de elcorteingles.es).
Para cada modelo de herramientas/precios-modelos.json con "comprasmartphone" (slug de su
página), toma las ofertas nuevas de la tienda "El Corte Inglés" de las capacidades del modelo.
Uso: python3 herramientas/precios_eci.py [--forzar]
"""
import datetime, json, re, sys, time, urllib.request
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Atlantic/Canary")
ahora = datetime.datetime.now(TZ)
if "--forzar" not in sys.argv and not ((ahora.weekday() == 0 and ahora.hour == 10) or (ahora.weekday() == 3 and ahora.hour == 13)):
    print("No es lunes 10:00 ni jueves 13:00 en Canarias:", ahora.isoformat()); sys.exit(0)

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
     "Accept-Language": "es-ES,es;q=0.9"}
TIENDA = "El Corte Inglés"

def pagina(slug):
    url = "https://comprasmartphone.com/telefonos/" + slug
    for intento in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=40) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            print("reintento", slug, e); time.sleep(5)
        except Exception as e:
            print("reintento", slug, e); time.sleep(5)
    return None

def tiendas(html):
    txt = "".join(json.loads(m.group(1)) for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', html))
    dec = json.JSONDecoder()
    for m in re.finditer(r'\{"data":\[\{"store":', txt):
        try:
            return dec.raw_decode(txt, m.start())[0]["data"]
        except Exception:
            continue
    return []

def capacidad(variante):
    m = re.search(r"(\d+)\s*(GB|TB)\s*$", variante or "", re.I)
    return (m.group(1) + m.group(2).upper()) if m else None

def eur(x):
    return (("%d" % x) if abs(x - round(x)) < 1e-9 else ("%.2f" % x).replace(".", ",")) + " €"

modelos = json.load(open("herramientas/precios-modelos.json"))
salida, leidas = {}, 0
for mid, m in modelos.items():
    slugs = m.get("comprasmartphone") or []
    if not slugs: continue
    caps = m.get("capacidades") or []
    mejor = {}
    for slug in slugs:
        html = pagina(slug)
        time.sleep(1.5)
        if not html: continue
        leidas += 1
        for t in tiendas(html):
            if (t.get("store") or {}).get("name") != TIENDA: continue
            for o in [t.get("headline_price")] + (t.get("additional_prices") or []):
                if not o or o.get("condition") != "new" or o.get("region", "ES") != "ES": continue
                cap = capacidad((o.get("product_variant") or {}).get("name"))
                if not cap or (caps and cap not in caps): continue
                precio = float(o.get("final_price") or o.get("price") or 0)
                if precio <= 0: continue
                d = o.get("data") or {}
                agotado = d.get("availability") not in (None, "in_stock")
                clave = (agotado, precio)
                if cap not in mejor or clave < mejor[cap][0]:
                    mejor[cap] = (clave, d.get("product_url") or o.get("url"), str(o.get("last_fetched_at", "")).lstrip("$D"))
    if not mejor: continue
    precios = sorted(v[0][1] for v in mejor.values())
    texto = eur(precios[0]) if precios[0] == precios[-1] else eur(precios[0]) + " – " + eur(precios[-1])
    primero = min(mejor.values(), key=lambda v: v[0][1])
    salida[mid] = {"precio": texto, "detalle": {c: v[0][1] for c, v in mejor.items()}, "url": primero[1],
                   "pack": False, "agotado": all(v[0][0] for v in mejor.values()),
                   "consultado": max(v[2] for v in mejor.values())}

print("páginas leídas:", leidas, "· modelos con precio:", len(salida))
if leidas < 10 or len(salida) < 5: raise SystemExit("Muy pocos datos: algo ha cambiado en comprasmartphone, no se actualiza")
json.dump({"canal": "eci_pen", "nombre": "El Corte Inglés Península", "fuente": "comprasmartphone.com",
           "actualizado": ahora.isoformat(timespec="minutes"), "modelos": salida},
          open("precios/eci_pen.json", "w"), ensure_ascii=False, indent=1)
