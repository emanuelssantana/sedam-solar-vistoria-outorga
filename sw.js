/* ============================================================================
   SERVICE WORKER - SEDAM-RO / SOLAR - FICHA DE VISTORIA V4
   Estrategia: cache-first para os arquivos do proprio app.
   Depois da primeira abertura com internet, o app abre em modo aviao.

   ATENCAO: Service Worker so funciona sob HTTPS ou localhost.
   Aberto como file:// direto do app Arquivos do iPhone ele NAO registra --
   nesse caso o app continua funcionando, mas o "abrir offline" fica por conta
   do cache comum do Safari. Os DADOS seguem seguros no IndexedDB nos dois casos.
   ============================================================================ */

const CACHE = 'sedam-outorga-v4-002';

const ARQUIVOS = [
  './',
  'FICHA_VISTORIA_INTERATIVA_OFFLINE_IPHONE_V4.html',
  'DASHBOARD_VISTORIAS_SEDAM.html',
  'manifest.webmanifest',
  'icone-180.png',
  'icone-192.png',
  'icone-512.png'
];

self.addEventListener('install', (ev) => {
  ev.waitUntil(
    caches.open(CACHE)
      // addAll falha inteiro se um arquivo faltar; por isso cada um vai sozinho
      .then(c => Promise.all(ARQUIVOS.map(a => c.add(a).catch(e => console.warn('SW: nao cacheou', a, e)))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (ev) => {
  ev.waitUntil(
    caches.keys()
      .then(nomes => Promise.all(nomes.filter(n => n !== CACHE).map(n => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (ev) => {
  const req = ev.request;

  // Nunca cacheia o envio para o Apps Script: sincronizacao tem que ser real.
  if (req.method !== 'GET' || req.url.indexOf('script.google.com') !== -1) return;

  ev.respondWith(
    caches.match(req).then(cacheado => {
      if (cacheado) return cacheado;
      return fetch(req)
        .then(resp => {
          if (resp && resp.status === 200 && resp.type === 'basic') {
            const copia = resp.clone();
            caches.open(CACHE).then(c => c.put(req, copia));
          }
          return resp;
        })
        .catch(() => cacheado);
    })
  );
});
