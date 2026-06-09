(function () {
  "use strict";

  var PAGES = [
    { id: "home", href: "index.html", key: "nav.home" },
    { id: "dashboard", href: "dashboard.html", key: "nav.dashboard" },
    { id: "booking", href: "booking.html", key: "nav.booking" },
    { id: "tracking", href: "delivery-map.html", key: "nav.tracking" },
    { id: "pricing", href: "pricing.html", key: "nav.pricing" },
    { id: "support", href: "support.html", key: "nav.support" },
    { id: "notifications", href: "notifications.html", key: "nav.notifications" },
    { id: "account", href: "account.html", key: "nav.account" },
  ];

  function t(key, fallback) {
    if (typeof RoustoI18n !== "undefined") return RoustoI18n.t(key) || fallback;
    return fallback;
  }

  function langQuery() {
    if (typeof RoustoI18n === "undefined") return "";
    return "?lang=" + RoustoI18n.locale;
  }

  function mountHeader(active) {
    var mount = document.getElementById("portalHeader");
    if (!mount) return;

    var links = PAGES.map(function (p) {
      var cls = p.id === active ? " active" : "";
      var label = t(p.key, p.key);
      return (
        '<a class="portal-nav-link' +
        cls +
        '" href="' +
        p.href +
        langQuery() +
        '">' +
        label +
        "</a>"
      );
    }).join("");

    var authAction =
      typeof RoustoConfig !== "undefined" && RoustoConfig.isLoggedIn
        ? '<button type="button" class="btn btn-ghost btn-sm" id="portalLogoutBtn">' +
          t("nav.logout", "Logout") +
          "</button>"
        : '<a href="login.html' +
          langQuery() +
          '" class="btn btn-ghost btn-sm">' +
          t("nav.login", "Login") +
          "</a>";

    var nextLang = typeof RoustoI18n !== "undefined" && RoustoI18n.locale === "ar" ? "en" : "ar";

    mount.innerHTML =
      '<header class="portal-header">' +
      '<div class="portal-header-inner">' +
      '<a href="index.html' +
      langQuery() +
      '" class="portal-brand">' +
      '<img src="../brand/logo.svg" alt="' +
      t("brand", "Rousto") +
      '" />' +
      "<span>" +
      t("brand", "Rousto") +
      "</span></a>" +
      '<nav class="portal-nav" id="portalNav">' +
      links +
      "</nav>" +
      '<div class="portal-header-actions">' +
      '<button type="button" class="btn btn-ghost btn-sm" id="langSwitchBtn">' +
      t("lang.switch", "English") +
      "</button>" +
      authAction +
      '<a href="booking.html' +
      langQuery() +
      '" class="btn btn-primary btn-sm">' +
      t("nav.bookNow", "Book now") +
      "</a>" +
      '<button class="portal-nav-toggle" id="portalNavToggle" aria-label="Menu">' +
      "<span></span><span></span><span></span></button>" +
      "</div></div></header>";

    var langBtn = document.getElementById("langSwitchBtn");
    if (langBtn && typeof RoustoI18n !== "undefined") {
      langBtn.addEventListener("click", function () {
        RoustoI18n.switchLocale(nextLang);
      });
    }

    var logoutBtn = document.getElementById("portalLogoutBtn");
    if (logoutBtn && typeof RoustoAPI !== "undefined") {
      logoutBtn.addEventListener("click", function () {
        RoustoAPI.logout().finally(function () {
          if (typeof RoustoToast === "function") {
            RoustoToast(t("nav.logout", "Logged out"));
          }
          window.location.href = "login.html" + langQuery();
        });
      });
    }

    var toggle = document.getElementById("portalNavToggle");
    var nav = document.getElementById("portalNav");
    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        nav.classList.toggle("open");
      });
      nav.querySelectorAll("a").forEach(function (a) {
        a.addEventListener("click", function () {
          nav.classList.remove("open");
        });
      });
    }
  }

  function mountConfigPanel() {
    var mount = document.getElementById("portalConfig");
    if (!mount || typeof RoustoConfig === "undefined") return;

    mount.innerHTML =
      '<details class="portal-config">' +
      "<summary>API settings (dev)</summary>" +
      '<div class="portal-config-grid">' +
      '<div><label for="cfgApiBase">API URL</label>' +
      '<input id="cfgApiBase" type="url" /></div>' +
      '<div><label for="cfgUserId">Customer ID</label>' +
      '<input id="cfgUserId" type="text" /></div>' +
      "</div>" +
      '<button type="button" class="btn btn-ghost btn-sm" id="cfgSaveBtn">' +
      t("common.save", "Save") +
      "</button>" +
      "</details>";

    var apiInput = document.getElementById("cfgApiBase");
    var userInput = document.getElementById("cfgUserId");
    if (apiInput) apiInput.value = RoustoConfig.apiBase;
    if (userInput) userInput.value = RoustoConfig.userId;

    var saveBtn = document.getElementById("cfgSaveBtn");
    if (saveBtn) {
      saveBtn.addEventListener("click", function () {
        RoustoConfig.apiBase = apiInput.value;
        RoustoConfig.userId = userInput.value;
        if (typeof RoustoToast === "function") {
          RoustoToast(t("common.save", "Saved"));
        }
        if (typeof window.onRoustoConfigSaved === "function") {
          window.onRoustoConfigSaved();
        }
      });
    }
  }

  function mountFooter() {
    var mount = document.getElementById("portalFooter");
    if (!mount) return;
    var q = langQuery();
    mount.innerHTML =
      '<footer class="portal-footer">' +
      '<div class="portal-footer-inner">' +
      "<span>© 2026 " +
      t("brand", "Rousto") +
      "</span>" +
      '<a href="privacy.html' +
      q +
      '">' +
      t("footer.privacy", "Privacy") +
      "</a>" +
      '<a href="terms.html' +
      q +
      '">' +
      t("footer.terms", "Terms") +
      "</a>" +
      '<a href="warranty.html' +
      q +
      '">' +
      t("footer.warranty", "Warranty") +
      "</a>" +
      '<a href="index.html' +
      q +
      '">' +
      t("nav.home", "Home") +
      "</a>" +
      "</div></footer>";
  }

  function init() {
    var active = document.body.getAttribute("data-portal-page") || "";
    var boot = function () {
      mountHeader(active);
      mountConfigPanel();
      mountFooter();
    };
    if (typeof RoustoI18n !== "undefined") {
      RoustoI18n.init().then(boot).catch(boot);
    } else {
      boot();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
