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

  function setConsent(value) {
    try {
      localStorage.setItem(KEY, value);
    } catch (_) {
      /* ignore */
    }
  }

  function showBanner() {
    if (getConsent()) return;
    var banner = document.getElementById("cookie-banner");
    if (!banner) return;
    banner.classList.add("visible");
  }

  function accept() {
    setConsent("all");
    var banner = document.getElementById("cookie-banner");
    if (banner) banner.classList.remove("visible");
    if (window.loadAdsense) window.loadAdsense();
  }

  function decline() {
    setConsent("essential");
    var banner = document.getElementById("cookie-banner");
    if (banner) banner.classList.remove("visible");
  }

  document.addEventListener("DOMContentLoaded", function () {
    var acceptBtn = document.getElementById("cookie-accept");
    var declineBtn = document.getElementById("cookie-decline");
    if (acceptBtn) acceptBtn.addEventListener("click", accept);
    if (declineBtn) declineBtn.addEventListener("click", decline);
    showBanner();
  });
})();
