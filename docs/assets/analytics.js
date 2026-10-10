'use strict';
// Google Analytics: count visits on the published site only.
(() => {
  if (location.hostname !== 'yasu1401.github.io' ||
      !location.pathname.startsWith('/ys-hm-photography/')) return;
  const measurementId = 'G-WE5TS5SCTP';
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', measurementId, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false
  });
  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + measurementId;
  document.head.append(tag);
})();
