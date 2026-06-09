(function () {
  "use strict";

  function apiBase() {
    if (typeof RoustoConfig !== "undefined") return RoustoConfig.apiBase;
    try {
      var cfg = JSON.parse(localStorage.getItem("rousto_web_config") || "{}");
      return (cfg.apiBase || "http://localhost:8000").replace(/\/$/, "");
    } catch (_) {
      return "http://localhost:8000";
    }
  }

  function fetchLanding(path) {
    return fetch(apiBase() + "/api/v1" + path)
      .then(function (res) {
        if (!res.ok) throw new Error("API " + res.status);
        return res.json();
      });
  }

  function renderHeroStats(stats, selector) {
    var el = document.querySelector(selector);
    if (!el || !stats.length) return;
    el.innerHTML = stats.map(function (s) {
      return '<div class="t"><b>' + s.value_ar + '</b><span>' + s.label_ar + '</span></div>';
    }).join("");
  }

  function renderStatsBand(stats, selector) {
    var el = document.querySelector(selector);
    if (!el || !stats.length) return;
    el.innerHTML = stats.map(function (s) {
      return '<div class="s reveal"><b>' + s.value_ar + '</b><span>' + s.label_ar + '</span></div>';
    }).join("");
    el.querySelectorAll(".reveal").forEach(function (node) {
      if ("IntersectionObserver" in window) {
        var io = new IntersectionObserver(function (entries) {
          entries.forEach(function (e) {
            if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
          });
        }, { threshold: 0.12 });
        io.observe(node);
      } else {
        node.classList.add("in");
      }
    });
  }

  function renderServices(services, gridSelector, selectSelector) {
    var grid = document.querySelector(gridSelector);
    if (grid && services.length) {
      grid.innerHTML = services.map(function (s) {
        return (
          '<article class="service-card reveal">' +
          '<div class="ic">' + (s.icon_emoji || "🔧") + '</div>' +
          '<h3>' + s.name_ar + '</h3>' +
          '<p>' + (s.subtitle_ar || "") + '</p>' +
          '<div class="price">' + s.price_label_ar + '</div>' +
          '<a class="link" href="#booking">احجز الآن ←</a>' +
          '</article>'
        );
      }).join("");
    }

    var select = document.querySelector(selectSelector);
    if (select && services.length) {
      select.innerHTML = services.map(function (s) {
        return '<option value="' + s.slug + '">' + s.name_ar + '</option>';
      }).join("");
    }
  }

  function renderMarketingPlans(plans, selector) {
    var el = document.querySelector(selector);
    if (!el || !plans.length) return;
    el.innerHTML = plans.map(function (p) {
      var badge = p.badge_ar ? '<span class="plan-badge">' + p.badge_ar + '</span>' : "";
      var featured = p.is_featured ? " pricing-card--featured" : "";
      var priceBlock = p.price_sar === 0
        ? '<div class="plan-price"><span class="plan-amount">مجاني</span></div>'
        : '<div class="plan-price"><span class="plan-amount">' + p.price_display_ar + '</span><span class="plan-period">' + p.price_label_ar + '</span></div>';
      var features = (p.features || []).map(function (f) {
        return '<li><span class="chk">✓</span>' + f + '</li>';
      }).join("");
      return (
        '<article class="pricing-card reveal' + featured + '">' + badge +
        '<h3>' + p.name_ar + '</h3>' +
        '<p class="plan-desc">' + (p.description_ar || "") + '</p>' +
        priceBlock +
        '<ul class="plan-features">' + features + '</ul>' +
        '<a href="' + (p.cta_url || "#booking") + '" class="btn ' + (p.is_featured ? "btn-primary" : "btn-ghost") + ' btn-block">' + p.cta_text_ar + '</a>' +
        '</article>'
      );
    }).join("");
  }

  function renderPackages(packages, selector) {
    var el = document.querySelector(selector);
    if (!el) return;
    if (!packages.length) {
      el.innerHTML = '<p class="muted">لا توجد باقات متاحة حالياً</p>';
      return;
    }
    el.innerHTML = packages.map(function (p) {
      return (
        '<article class="package-card reveal">' +
        '<h4>' + p.name_ar + '</h4>' +
        '<p>' + (p.description_ar || "") + '</p>' +
        '<div class="package-price">' + p.price_sar + ' دينار</div>' +
        '<div class="package-meta">' + p.visits_count + ' زيارات · صالحة ' + p.validity_days + ' يوم</div>' +
        '<div class="package-save">وفّر ' + p.savings_sar + ' دينار</div>' +
        '<a href="#booking" class="btn btn-ghost btn-sm btn-block">اشتري الباقة</a>' +
        '</article>'
      );
    }).join("");
  }

  function renderFeatures(features, selector) {
    var el = document.querySelector(selector);
    if (!el || !features.length) return;
    el.innerHTML = features.map(function (f) {
      return (
        '<li><span class="chk">' + (f.icon || "✓") + '</span>' +
        '<div><b>' + f.title_ar + '</b><span>' + (f.description_ar || "") + '</span></div></li>'
      );
    }).join("");
  }

  function showFallback() {
    var notice = document.getElementById("pricingApiNotice");
    if (notice) notice.style.display = "block";
  }

  function initIndex() {
    fetchLanding("/landing/page")
      .then(function (body) {
        var data = body.data;
        renderHeroStats(data.hero.stats, ".hero-trust");
        renderStatsBand(data.hero.stats, ".stats");
        renderServices(data.pricing.services, ".services-grid", "#service");
        renderMarketingPlans(data.pricing.marketing_plans, "#pricingPlans");
        renderFeatures(data.features, ".feature-list");
      })
      .catch(showFallback);
  }

  function initPricingPage() {
    fetchLanding("/landing/pricing")
      .then(function (body) {
        var data = body.data;
        renderServices(data.services, "#pricingServices", "#pricingServiceSelect");
        renderMarketingPlans(data.marketing_plans, "#pricingPlans");
        renderPackages(data.packages, "#pricingPackages");
      })
      .catch(showFallback);

    fetchLanding("/landing/page")
      .then(function (body) {
        renderHeroStats(body.data.hero.stats, "#pricingHeroStats");
      })
      .catch(function () {});
  }

  if (document.getElementById("pricingPlans") || document.querySelector(".services-grid")) {
    if (document.getElementById("pricingPage")) {
      initPricingPage();
    } else {
      initIndex();
    }
  }
})();
