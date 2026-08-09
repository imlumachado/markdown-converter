(function () {
  "use strict";

  var KEY = "mdconverter-cookie-consent";

  function getConsent() {
    try {
      return localStorage.getItem(KEY);
    } catch (_) {
      return null;
    }
  }

  function canShowAds() {
    return getConsent() === "all";
  }

  window.loadAdsense = function () {
    var existing = document.querySelector("script[data-adsense]");
    if (existing) return;
    var adSlot = document.getElementById("ad-slot");
    if (!adSlot) return;
    adSlot.hidden = false;
    if (window.adsbygoogle) {
      try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (_) { /* ignore */ }
      return;
    }
    var script = document.createElement("script");
    script.async = true;
    script.dataset.adsense = "1";
    script.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" +
      (adSlot.dataset.client || "");
    script.crossOrigin = "anonymous";
    document.head.appendChild(script);
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (_) { /* ignore */ }
  };

  document.addEventListener("DOMContentLoaded", function () {
    if (canShowAds()) window.loadAdsense();
  });
})();
