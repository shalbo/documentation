(function (global) {
  "use strict";

  var STORAGE_KEY = "rousto_locale";
  var SUPPORTED = ["ar", "en"];
  var DEFAULT_LOCALE = "ar";
  var _dict = {};
  var _locale = DEFAULT_LOCALE;
  var _ready = null;

  function detectFromPath() {
    var parts = window.location.pathname.split("/").filter(Boolean);
    var webIdx = parts.indexOf("web");
    if (webIdx >= 0 && parts[webIdx + 1] && SUPPORTED.indexOf(parts[webIdx + 1]) >= 0) {
      return parts[webIdx + 1];
    }
    return null;
  }

  function detectLocale() {
    var params = new URLSearchParams(window.location.search);
    var q = params.get("lang");
    if (q && SUPPORTED.indexOf(q) >= 0) return q;
    var pathLang = detectFromPath();
    if (pathLang) return pathLang;
    try {
      var stored = localStorage.getItem(STORAGE_KEY);
      if (stored && SUPPORTED.indexOf(stored) >= 0) return stored;
    } catch (_) {}
    var browser = (navigator.language || "").split("-")[0];
    return SUPPORTED.indexOf(browser) >= 0 ? browser : DEFAULT_LOCALE;
  }

  function applyDocumentLocale() {
    document.documentElement.lang = _locale;
    document.documentElement.dir = _locale === "ar" ? "rtl" : "ltr";
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      var text = t(key);
      if (text) el.textContent = text;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach(function (el) {
      var key = el.getAttribute("data-i18n-placeholder");
      var text = t(key);
      if (text) el.setAttribute("placeholder", text);
    });
  }

  function loadDict(locale) {
    return fetch("i18n/" + locale + ".json")
      .then(function (res) {
        if (!res.ok) throw new Error("i18n load failed");
        return res.json();
      })
      .then(function (dict) {
        _dict = dict;
        _locale = locale;
        try {
          localStorage.setItem(STORAGE_KEY, locale);
        } catch (_) {}
        applyDocumentLocale();
        return dict;
      });
  }

  function init() {
    if (_ready) return _ready;
    _locale = detectLocale();
    _ready = loadDict(_locale);
    return _ready;
  }

  function t(key) {
    return _dict[key] || key;
  }

  function get locale() {
    return _locale;
  }

  function switchLocale(next) {
    if (SUPPORTED.indexOf(next) < 0) return Promise.resolve();
    var url = new URL(window.location.href);
    url.searchParams.set("lang", next);
    window.location.href = url.toString();
    return Promise.resolve();
  }

  function localizedPath(page) {
    return page + (page.indexOf("?") >= 0 ? "&" : "?") + "lang=" + _locale;
  }

  global.RoustoI18n = {
    init: init,
    t: t,
    get locale() {
      return _locale;
    },
    switchLocale: switchLocale,
    localizedPath: localizedPath,
    applyDocumentLocale: applyDocumentLocale,
  };
})(window);
