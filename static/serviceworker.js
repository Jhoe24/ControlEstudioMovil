self.addEventListener('install', function(event) {
  self.skipWaiting();
  console.log('Service Worker instalado');
});

self.addEventListener('activate', function(event) {
  // Service Worker activado
  console.log('Service Worker activado');
});