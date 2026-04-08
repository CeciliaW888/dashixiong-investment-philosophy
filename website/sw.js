const CACHE_VERSION = 2;
const CACHE_NAME = `dashixiong-study-v${CACHE_VERSION}`;
const OFFLINE_URL = './offline.html';

const MODULE_URLS = [
  './modules/01-why-economics.html',
  './modules/02-historical-pricing.html',
  './modules/03-great-navigation.html',
  './modules/04-capital-government.html',
  './modules/05-austrian-vs-keynesian.html',
  './modules/06-monetary-expansion.html',
  './modules/07-week1-review.html',
  './modules/08-etf-essentials.html',
  './modules/09-gold-pricing.html',
  './modules/10-oil-new-energy.html',
  './modules/11-digital-economy.html',
  './modules/12-three-part-method.html',
  './modules/13-valuation-cases.html',
  './modules/14-week2-review.html',
  './modules/15-market-cycles.html',
  './modules/16-long-term-holding.html',
  './modules/17-china-us-dynamics.html',
  './modules/18-argentina-japan.html',
  './modules/19-ai-investment.html',
  './modules/20-six-assets.html',
  './modules/21-final-framework.html'
];

const DATA_URLS = [
  './data/flashcards.json',
  './data/quiz-01.json',
  './data/quiz-02.json',
  './data/quiz-03.json',
  './data/quiz-04.json',
  './data/quiz-05.json',
  './data/quiz-06.json',
  './data/quiz-07.json',
  './data/quiz-08.json',
  './data/quiz-09.json',
  './data/quiz-10.json',
  './data/quiz-11.json',
  './data/quiz-12.json',
  './data/quiz-13.json',
  './data/quiz-14.json',
  './data/quiz-15.json',
  './data/quiz-16.json',
  './data/quiz-17.json',
  './data/quiz-18.json',
  './data/quiz-19.json',
  './data/quiz-20.json',
  './data/quiz-21.json'
];

const DIAGRAM_URLS = [
  './diagrams/01-monetary-evolution.svg',
  './diagrams/02-gold-five-contradictions.svg',
  './diagrams/03-six-assets-network.svg',
  './diagrams/04-three-part-method.svg',
  './diagrams/05-policy-vs-real-bull.svg',
  './diagrams/06-china-us-financial.svg'
];

const ICON_URLS = [
  './icons/apple-touch-icon-180.png',
  './icons/icon-192.png',
  './icons/icon-192-maskable.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png'
];

const PRECACHE_URLS = [
  './',
  './index.html',
  './offline.html',
  './manifest.json',
  './styles.css',
  './main.js',
  ...ICON_URLS,
  ...MODULE_URLS,
  ...DATA_URLS,
  ...DIAGRAM_URLS
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames
          .filter(name => name.startsWith('dashixiong-study-') && name !== CACHE_NAME)
          .map(name => caches.delete(name))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
          return response;
        })
        .catch(() => caches.match(request).then(cached => cached || caches.match(OFFLINE_URL)))
    );
    return;
  }

  if (url.origin === self.location.origin) {
    event.respondWith(
      (async () => {
        const cache = await caches.open(CACHE_NAME);
        const cached = await cache.match(request);
        const fetchPromise = fetch(request).then(response => {
          if (response.ok) cache.put(request, response.clone());
          return response;
        }).catch(() => null);
        return cached || fetchPromise || caches.match(OFFLINE_URL);
      })()
    );
    return;
  }

  event.respondWith(
    (async () => {
      const cached = await caches.match(request);
      if (cached) return cached;
      try {
        const response = await fetch(request);
        if (response.ok) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(request, response.clone());
        }
        return response;
      } catch {
        return new Response('', { status: 408, statusText: 'Offline' });
      }
    })()
  );
});
