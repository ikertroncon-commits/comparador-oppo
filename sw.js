// Service worker del Comparador OPPO.
// Los datos siempre vienen en vivo de Firebase; aqui solo se guardan la app y las fotos
// para que abra rapido y muestre algo aunque falle la conexion un momento.
const CACHE = "comparador-v4";
const SHELL = ["./", "./index.html", "./manifest.json", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  const url = new URL(req.url);
  // Solo archivos propios (app, iconos, fotos). Firebase y Google van directos a la red.
  if (req.method !== "GET" || url.origin !== self.location.origin) return;
  // Primero la red (siempre la version mas nueva); si falla, la copia guardada.
  e.respondWith(
    // "no-cache": pregunta siempre al servidor si hay version nueva (evita esperar 10 min)
    (req.mode === "navigate" || /\.(html|json|js)$|\/$/.test(url.pathname) ? fetch(req.url, { cache: "no-cache" }) : fetch(req)).then((res) => {
      if (res.ok) { const copy = res.clone(); caches.open(CACHE).then((c) => c.put(req, copy)); }
      return res;
    }).catch(() => caches.match(req).then((r) => r || caches.match("./index.html")))
  );
});
