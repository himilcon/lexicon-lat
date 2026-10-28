/* Service worker: guarda a aplicação, o índice, os verbetes abertos e os textos para uso offline.
   O corpo dos verbetes (data/ls/NNN.json, 53 MB no total) é guardado à medida que é consultado. */
const VERSION = "lt-v4";                    // aplicação: mude a cada alteração de HTML/CSS/JS
const DATA_CACHE = "lt-data-ls-2026-10-1";  // dicionário: mude junto com DATA_VER em app.js
const TEXT_CACHE = "lt-textos";
const SHELL = ["./", "index.html", "styles.css", "app.js", "reader.js", "manifest.webmanifest",
  "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png"];
const INDEX = "data/index.json?v=ls-2026-10-1";
const KEEP = [VERSION, DATA_CACHE, TEXT_CACHE];

self.addEventListener("install", ev => {
  ev.waitUntil(Promise.all([
    caches.open(VERSION).then(c => c.addAll(SHELL)),
    caches.open(DATA_CACHE).then(async c => { if (!(await c.match(INDEX))) await c.add(INDEX); }),
  ]).then(() => self.skipWaiting()));
});

self.addEventListener("activate", ev => {
  ev.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => !KEEP.includes(k)).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

function cacheFirst(req, name) {
  return caches.open(name).then(async c => {
    const hit = await c.match(req);
    if (hit) return hit;
    const res = await fetch(req);
    if (res.ok) c.put(req, res.clone());
    return res;
  });
}

function networkFirst(req, name, key) {
  return caches.open(name).then(c => fetch(req)
    .then(res => { if (res.ok) c.put(key, res.clone()); return res; })
    .catch(() => c.match(key)));
}

self.addEventListener("fetch", ev => {
  const url = new URL(ev.request.url);
  if (ev.request.method !== "GET") return;
  const p = url.pathname;
  // Índice, verbetes e formas: cache primeiro (a versão vai na query)
  if (p.endsWith("/data/index.json") || p.includes("/data/ls/") || p.endsWith("/data/formas.json")) {
    ev.respondWith(cacheFirst(ev.request, DATA_CACHE)); return;
  }
  // Camada PT e lista de textos: rede primeiro, para que atualizações apareçam logo; cache se offline
  if (p.endsWith("/data/pt.json") || p.endsWith("/textos/index.json")) {
    ev.respondWith(networkFirst(ev.request, p.endsWith("pt.json") ? DATA_CACHE : TEXT_CACHE, p)); return;
  }
  // Textos: cache primeiro (versionados); ao guardar uma versão nova, descarta as anteriores do mesmo texto
  if (p.includes("/textos/")) {
    ev.respondWith(caches.open(TEXT_CACHE).then(async c => {
      const hit = await c.match(ev.request);
      if (hit) return hit;
      const res = await fetch(ev.request);
      if (res.ok) {
        for (const k of await c.keys()) if (new URL(k.url).pathname === p) await c.delete(k);
        await c.put(ev.request, res.clone());
      }
      return res;
    }));
    return;
  }
  // Aplicação e fontes: usa o cache e atualiza em segundo plano
  if (url.origin === location.origin || url.hostname.endsWith("fonts.googleapis.com") || url.hostname.endsWith("fonts.gstatic.com")) {
    ev.respondWith(caches.open(VERSION).then(async c => {
      const hit = await c.match(ev.request, { ignoreSearch: url.origin === location.origin && !url.search.includes("v=") });
      const net = fetch(ev.request).then(res => { if (res.ok || res.type === "opaque") c.put(ev.request, res.clone()); return res; }).catch(() => hit);
      return hit || net;
    }));
  }
});
