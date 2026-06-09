const STORAGE_KEY = "rousto_delivery_map_config";

const state = {
  apiBase: "http://localhost:8000",
  userId: "a0000000-0000-4000-8000-000000000001",
  pollTimer: null,
  mapData: null,
};

function $(id) {
  return document.getElementById(id);
}

function loadConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    if (saved.apiBase) state.apiBase = saved.apiBase;
    if (saved.userId) state.userId = saved.userId;
  } catch (_) {}
  $("apiBase").value = state.apiBase;
  $("userId").value = state.userId;
}

function saveConfig() {
  state.apiBase = $("apiBase").value.replace(/\/$/, "");
  state.userId = $("userId").value.trim();
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ apiBase: state.apiBase, userId: state.userId })
  );
}

function toast(msg) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast show";
  setTimeout(() => el.classList.remove("show"), 2400);
}

async function fetchDeliveryMap() {
  saveConfig();
  const res = await fetch(`${state.apiBase}/api/v1/bookings/active/delivery-map`, {
    headers: { "X-User-Id": state.userId },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body?.error?.message || `خطأ ${res.status}`);
  }
  return body.data;
}

function renderMap(data) {
  const host = $("mapView");
  const points = [];

  if (data.customer_location) {
    points.push({ type: "home", ...data.customer_location });
  }
  (data.trail || []).forEach((p) => points.push({ type: "trail", lat: p.lat, lng: p.lng }));
  if (data.technician?.location) {
    points.push({ type: "tech", ...data.technician.location });
  }

  if (!points.length) {
    host.innerHTML = '<div class="map-empty">لا توجد بيانات خريطة</div>';
    return;
  }

  const lats = points.map((p) => p.lat);
  const lngs = points.map((p) => p.lng);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);
  const latSpan = Math.max(maxLat - minLat, 0.0001);
  const lngSpan = Math.max(maxLng - minLng, 0.0001);
  const normX = (lng) => ((lng - minLng) / lngSpan) * 100;
  const normY = (lat) => 100 - ((lat - minLat) / latSpan) * 100;

  const markers = points
    .map((p) => {
      const left = normX(p.lng).toFixed(1);
      const top = normY(p.lat).toFixed(1);
      const cls =
        p.type === "tech"
          ? "map-marker-tech"
          : p.type === "home"
            ? "map-marker-home"
            : "map-marker-trail";
      const icon = p.type === "tech" ? "🚐" : p.type === "home" ? "🏠" : "";
      return `<div class="map-marker ${cls}" style="left:calc(${left}% - 12px);top:calc(${top}% - 12px)">${icon}</div>`;
    })
    .join("");

  host.innerHTML = `<div class="map-road"></div>${markers}`;
}

function renderSteps(steps) {
  const list = $("stepsList");
  if (!steps?.length) {
    list.innerHTML = "<li>لا توجد مراحل</li>";
    return;
  }
  list.innerHTML = steps
    .map((s) => {
      const dotClass = s.is_done ? "done" : s.is_current ? "current" : "";
      const time = s.occurred_at
        ? new Date(s.occurred_at).toLocaleTimeString("ar-SA", {
            hour: "2-digit",
            minute: "2-digit",
          })
        : "قريباً";
      return `<li><span class="step-dot ${dotClass}"></span><div><strong>${s.label_ar}</strong><br><small>${time}</small></div></li>`;
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
    data.distance_km != null ? `${data.distance_km} كم` : "—";
  $("etaMinutes").textContent =
    data.eta_minutes != null ? `${data.eta_minutes} دقيقة` : "—";

  const progress = data.progress_percent;
  $("progressPercent").textContent =
    progress != null ? `${progress}%` : "—";
  $("progressBar").style.width = progress != null ? `${progress}%` : "0%";

  renderMap(data);
  renderSteps(data.steps);

  const tech = data.technician;
  if (tech) {
    $("technicianCard").innerHTML = `
      <div class="tech-avatar">${tech.avatar_initials || tech.full_name.charAt(0)}</div>
      <div class="tech-meta">
        <strong>${tech.full_name}</strong><br>
        <small>★ ${tech.rating}${tech.eta_minutes ? ` · ${tech.eta_minutes} د` : ""}</small>
      </div>`;
  } else {
    $("technicianCard").textContent = "لم يُعيَّن فني بعد";
  }

  schedulePolling(data);
}

function schedulePolling(data) {
  if (state.pollTimer) clearInterval(state.pollTimer);
  if (!data?.is_live || !data.refresh_interval_seconds) return;
  state.pollTimer = setInterval(() => {
    refresh().catch(() => {});
  }, data.refresh_interval_seconds * 1000);
}

async function refresh() {
  const data = await fetchDeliveryMap();
  renderAll(data);
  toast("تم التحديث");
}

$("refreshBtn").addEventListener("click", () => {
  refresh().catch((e) => toast(e.message));
});

loadConfig();
refresh().catch((e) => toast(e.message));
