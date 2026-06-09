(function () {
  "use strict";

  var state = { pollTimer: null, mapData: null };

  function $(id) {
    return document.getElementById(id);
  }

  function renderMap(data) {
    var host = $("mapView");
    var points = [];

    if (data.customer_location) {
      points.push(Object.assign({ type: "home" }, data.customer_location));
    }
    (data.trail || []).forEach(function (p) {
      points.push({ type: "trail", lat: p.lat, lng: p.lng });
    });
    if (data.technician && data.technician.location) {
      points.push(Object.assign({ type: "tech" }, data.technician.location));
    }

    if (!points.length) {
      host.innerHTML = '<div class="map-empty">لا توجد بيانات خريطة</div>';
      return;
    }

    var lats = points.map(function (p) {
      return p.lat;
    });
    var lngs = points.map(function (p) {
      return p.lng;
    });
    var minLat = Math.min.apply(null, lats);
    var maxLat = Math.max.apply(null, lats);
    var minLng = Math.min.apply(null, lngs);
    var maxLng = Math.max.apply(null, lngs);
    var latSpan = Math.max(maxLat - minLat, 0.0001);
    var lngSpan = Math.max(maxLng - minLng, 0.0001);
    var normX = function (lng) {
      return ((lng - minLng) / lngSpan) * 100;
    };
    var normY = function (lat) {
      return 100 - ((lat - minLat) / latSpan) * 100;
    };

    var markers = points
      .map(function (p) {
        var left = normX(p.lng).toFixed(1);
        var top = normY(p.lat).toFixed(1);
        var cls =
          p.type === "tech"
            ? "map-marker-tech"
            : p.type === "home"
              ? "map-marker-home"
              : "map-marker-trail";
        var icon = p.type === "tech" ? "🚐" : p.type === "home" ? "🏠" : "";
        return (
          '<div class="map-marker ' + cls + '" style="left:calc(' + left +
          "% - 12px);top:calc(" + top + '% - 12px)">' + icon + "</div>"
        );
      })
      .join("");

    host.innerHTML = '<div class="map-road"></div>' + markers;
  }

  function renderSteps(steps) {
    var list = $("stepsList");
    if (!steps || !steps.length) {
      list.innerHTML = "<li>لا توجد مراحل</li>";
      return;
    }
    list.innerHTML = steps
      .map(function (s) {
        var dotClass = s.is_done ? "done" : s.is_current ? "current" : "";
        var time = s.occurred_at
          ? new Date(s.occurred_at).toLocaleTimeString("ar-SA", {
              hour: "2-digit",
              minute: "2-digit",
            })
          : "قريباً";
        return (
          "<li><span class='step-dot " + dotClass + "'></span><div><strong>" +
          s.label_ar + "</strong><br><small>" + time + "</small></div></li>"
        );
      })
      .join("");
  }

  function renderAll(data) {
    if (!data) {
      $("phaseLabel").textContent = "لا يوجد حجز نشط";
      $("bookingRef").textContent = "—";
      return;
    }

    state.mapData = data;
    $("phaseLabel").textContent = data.delivery_phase_label_ar;
    $("bookingRef").textContent = data.booking.reference;
    $("distanceKm").textContent =
      data.distance_km != null ? data.distance_km + " كم" : "—";
    $("etaMinutes").textContent =
      data.eta_minutes != null ? data.eta_minutes + " دقيقة" : "—";

    var progress = data.progress_percent;
    $("progressPercent").textContent = progress != null ? progress + "%" : "—";
    $("progressBar").style.width = progress != null ? progress + "%" : "0%";

    renderMap(data);
    renderSteps(data.steps);

    var tech = data.technician;
    if (tech) {
      $("technicianCard").innerHTML =
        '<div class="tech-avatar">' + (tech.avatar_initials || tech.full_name.charAt(0)) + "</div>" +
        '<div class="tech-meta"><strong>' + tech.full_name + "</strong><br>" +
        "<small>★ " + tech.rating +
        (tech.eta_minutes ? " · " + tech.eta_minutes + " د" : "") +
        "</small></div>";
    } else {
      $("technicianCard").textContent = "لم يُعيَّن فني بعد";
    }

    schedulePolling(data);
  }

  function schedulePolling(data) {
    if (state.pollTimer) clearInterval(state.pollTimer);
    if (!data || !data.is_live || !data.refresh_interval_seconds) return;
    state.pollTimer = setInterval(function () {
      refresh().catch(function () {});
    }, data.refresh_interval_seconds * 1000);
  }

  async function refresh() {
    var res = await RoustoAPI.getActiveDeliveryMap();
    renderAll(res.data);
    RoustoToast("تم التحديث");
  }

  $("refreshBtn").addEventListener("click", function () {
    refresh().catch(function (e) {
      RoustoToast(e.message, "error");
    });
  });

  window.onRoustoConfigSaved = refresh;
  refresh().catch(function (e) {
    RoustoToast(e.message, "error");
  });
})();
