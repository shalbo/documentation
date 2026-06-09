(function () {
  "use strict";

  var PAGES = [
    { id: "home", href: "index.html", label: "الرئيسية" },
    { id: "dashboard", href: "dashboard.html", label: "لوحتي" },
    { id: "booking", href: "booking.html", label: "احجز" },
    { id: "tracking", href: "delivery-map.html", label: "تتبّع" },
    { id: "pricing", href: "pricing.html", label: "الأسعار" },
    { id: "support", href: "support.html", label: "الدعم" },
    { id: "account", href: "account.html", label: "حسابي" },
  ];

  function mountHeader(active) {
    var mount = document.getElementById("portalHeader");
    if (!mount) return;

    var links = PAGES.map(function (p) {
      var cls = p.id === active ? " active" : "";
      return '<a class="portal-nav-link' + cls + '" href="' + p.href + '">' + p.label + "</a>";
    }).join("");

    mount.innerHTML =
      '<header class="portal-header">' +
      '<div class="portal-header-inner">' +
      '<a href="index.html" class="portal-brand">' +
      '<img src="../brand/logo.svg" alt="روستو" />' +
      "<span>روستو</span></a>" +
      '<nav class="portal-nav" id="portalNav">' + links + "</nav>" +
      '<div class="portal-header-actions">' +
      '<a href="booking.html" class="btn btn-primary btn-sm">احجز الآن</a>' +
      '<button class="portal-nav-toggle" id="portalNavToggle" aria-label="القائمة">' +
      "<span></span><span></span><span></span></button>" +
      "</div></div></header>";

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
      "<summary>إعدادات الاتصال (تطوير)</summary>" +
      '<div class="portal-config-grid">' +
      '<div><label for="cfgApiBase">عنوان API</label>' +
      '<input id="cfgApiBase" type="url" /></div>' +
      '<div><label for="cfgUserId">معرّف العميل</label>' +
      '<input id="cfgUserId" type="text" /></div>' +
      "</div>" +
      '<button type="button" class="btn btn-ghost btn-sm" id="cfgSaveBtn">حفظ</button>' +
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
          RoustoToast("تم حفظ الإعدادات");
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
    mount.innerHTML =
      '<footer class="portal-footer">' +
      '<div class="portal-footer-inner">' +
      "<span>© 2026 روستو — عناية ذكية بسيارتك</span>" +
      '<a href="index.html">الموقع الرئيسي</a>' +
      "</div></footer>";
  }

  function init() {
    var active = document.body.getAttribute("data-portal-page") || "";
    mountHeader(active);
    mountConfigPanel();
    mountFooter();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
