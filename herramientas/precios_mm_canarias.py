"""Precios de MediaMarkt Canarias (tienda Shopify) -> precios/mm_can.json

Lee el catálogo público de móviles de canarias.mediamarkt.es y, para cada modelo de
herramientas/precios-modelos.json, busca el producto por su nombre ("mm_can") y las
capacidades del modelo. Solo unidades nuevas; prefiere las que tienen stock y, si el móvil
solo está en pack ("Bundle"), usa el pack.
Uso: python3 herramientas/precios_mm_canarias.py [--forzar]
"""
import datetime, json, re, sys, time, urllib.request
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Atlantic/Canary")
ahora = datetime.datetime.now(TZ)
# GitHub programa en hora UTC: se lanza a las dos horas posibles y aquí se comprueba la hora de Canarias
if "--forzar" not in sys.argv and not ((ahora.weekday() == 0 and ahora.hour == 10) or (ahora.weekday() == 3 and ahora.hour == 13)):
    print("No es lunes 10:00 ni jueves 13:00 en Canarias:", ahora.isoformat()); sys.exit(0)

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
BASE = "https://canarias.mediamarkt.es"

def get(url):
    for intento in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print("reintento", url, e); time.sleep(5)
    raise SystemExit("No se pudo leer " + url)

productos = []
for page in range(1, 40):
    ps = get(f"{BASE}/collections/smartphones/products.json?limit=250&page={page}").get("products", [])
    productos += ps
    if len(ps) < 250: break
print("productos leídos:", len(productos))
if len(productos) < 100: raise SystemExit("Catálogo sospechosamente pequeño: no se actualiza")

def nombre(t):
    n = t.split(",")[0].strip().lower()
    n = re.sub(r"^móvil\s*-\s*", "", n)
    bundle = " bundle " in f" {n} "
    n = re.sub(r"\bbundle\s+", "", n)
    return re.sub(r"\s+", " ", n).strip(), bundle

def capacidad(t):
    for parte in [x.strip() for x in t.split(",")[1:]]:
        if "RAM" in parte.upper(): continue
        m = re.fullmatch(r"(\d+)\s*(GB|TB)", parte, re.I)
        if m: return m.group(1) + m.group(2).upper()
    return None

def eur(x):
    return (("%d" % x) if abs(x - round(x)) < 1e-9 else ("%.2f" % x).replace(".", ",")) + " €"

modelos = json.load(open("herramientas/precios-modelos.json"))
salida = {}
for mid, m in modelos.items():
    nombres = [n.lower() for n in m.get("mm_can", [])]
    if not nombres: continue
    caps = m.get("capacidades") or []
    mejor = {"normal": {}, "bundle": {}, "normal_agotado": {}, "bundle_agotado": {}}
    for p in productos:
        t = p.get("title", "")
        if re.search(r"reacondicionad|seminuevo|outlet", t, re.I): continue
        n, bundle = nombre(t)
        if n not in nombres: continue
        cap = capacidad(t)
        if caps and cap not in caps: continue
        for v in p.get("variants", []):
            precio = float(v.get("price") or 0)
            if precio <= 0: continue
            dest = mejor[("bundle" if bundle else "normal") + ("" if v.get("available") else "_agotado")]
            if cap not in dest or precio < dest[cap][0]:
                dest[cap] = (precio, f"{BASE}/products/{p.get('handle')}")
    # primero lo que tiene stock; si no hay stock, el precio publicado igualmente
    orden = ["normal", "bundle", "normal_agotado", "bundle_agotado"]
    clave = next((k for k in orden if mejor[k]), None)
    if not clave: continue
    elegido = mejor[clave]
    precios = sorted(v[0] for v in elegido.values())
    texto = eur(precios[0]) if precios[0] == precios[-1] else eur(precios[0]) + " – " + eur(precios[-1])
    primero = min(elegido.values())
    salida[mid] = {"precio": texto, "detalle": {c: v[0] for c, v in elegido.items()}, "url": primero[1],
                   "pack": clave.startswith("bundle"), "agotado": clave.endswith("agotado")}

if len(salida) < 10: raise SystemExit(f"Solo {len(salida)} modelos con precio: algo ha cambiado en la web, no se actualiza")
json.dump({"canal": "mm_can", "nombre": "MediaMarkt Canarias", "actualizado": ahora.isoformat(timespec="minutes"),
           "modelos": salida}, open("precios/mm_can.json", "w"), ensure_ascii=False, indent=1)
print("modelos con precio:", len(salida))
