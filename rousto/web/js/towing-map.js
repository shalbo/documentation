const STORAGE_KEY = "rousto_towing_map_config";

const state = { apiBase: "http://localhost:8000", userId: "", pollTimer: null, data: null };

function $(id) { return document.getElementById(id); }

function loadConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    if (saved.apiBase) state.apiBase = saved.apiBase;
    if (saved.userId) state.userId = saved.userId;
  } catch (_) {}
  $("apiBase").value = state.apiBase;
  $("userId").value = state.userId || "a0000000-0000-4000-8000-000000000001";
}

function saveConfig() {
  state.apiBase = $("apiBase").value.replace(/\/$/, "");
  state.userId = $("userId").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase: state.apiBase, userId: state.userId }));
}

function toast(msg) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast show";
  setTimeout(() => el.classList.remove("show"), 2400);
}

async function fetchMap() {
  saveConfig();
  const res = await fetch(`${state.apiBase}/api/v1/towing/dispatches/active/map`, {
    headers: { "X-User-Id": state.userId },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.error?.message || `خطأ ${res.status}`);
  return body.data;
}

function renderMap(data) {
  const host = $("mapView");
  const points = [];
  if (data.pickup) points.push({ ...data.pickup, type: "pickup", icon: "⚠️" });
  if (data.dropoff) points.push({ ...data.dropoff, type: "dropoff", icon: "🏭" });
  (data.trail || []).forEach((p) => points.push({ ...p, type: "trail" }));
  if (data.tow_truck?.location) points.push({ ...data.tow_truck.location, type: "truck", icon: "🚛" });

  if (!points.length) {
    host.innerHTML = '<div class="map-empty">لا توجد بيانات</div>';
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

  host.innerHTML = points.map((p) => {
    const left = normX(p.lng).toFixed(1);
    const top = normY(p.lat).toFixed(1);
    const size = p.type === "trail" ? 8 : 28;
    const bg = p.type === "pickup" ? "#B07D00" : p.type === "dropoff" ? "#15161A" : p.type === "truck" ? "#E11B22" : "#1E9E6A";
    return `<div class="map-marker" style="position:absolute;left:calc(${left}% - ${size/2}px);top:calc(${top}% - ${size/2}px);width:${size}px;height:${size}px;border-radius:50%;background:${bg};display:grid;place-items:center;color:#fff;font-size:.7rem">${p.icon || ""}</div>`;
  }).join("");
  host.style.position = "relative";
}

function renderAll(data) {
  if (!data) {
    $("phaseLabel").textContent = "لا يوجد طلب سحب نشط";
    return;
  }
  state.data = data;
  $("phaseLabel").textContent = data.dispatch.dispatch_phase_label_ar;
  $("dispatchRef").textContent = data.dispatch.reference;
  $("distanceKm").textContent = data.distance_km != null ? `${data.distance_km} كم` : "—";
  $("etaMinutes").textContent = data.eta_minutes != null ? `${data.eta_minutes} د` : "—";
  $("progressPercent").textContent = data.progress_percent != null ? `${data.progress_percent}%` : "—";
  $("progressBar").style.width = data.progress_percent != null ? `${data.progress_percent}%` : "0%";
  $("legInfo").textContent = data.active_leg === "to_pickup"
    ? `المرحلة: التوجّه لموقع العطل — ${data.pickup.label}`
    : data.active_leg === "to_dropoff"
      ? `المرحلة: نقل السيارة — ${data.dropoff.label}`
      : "—";

  renderMap(data);

  const driver = data.tow_truck;
  $("driverCard").innerHTML = driver
    ? `<div class="tech-avatar">${driver.avatar_initials || driver.full_name.charAt(0)}</div>
       <div class="tech-meta"><strong>${driver.full_name}</strong><br><small>★ ${driver.rating}</small></div>`
    : "بانتظار تعيين السطحة";

  const list = $("stepsList");
  list.innerHTML = (data.steps || []).map((s) => {
    const dot = s.is_done ? "done" : s.is_current ? "current" : "";
    const time = s.occurred_at ? new Date(s.occurred_at).toLocaleTimeString("ar-SA", { hour: "2-digit", minute: "2-digit" }) : "قريباً";
    return `<li><span class="step-dot ${dot}"></span><div><strong>${s.label_ar}</strong><br><small>${time}</small></div></li>`;
  }).join("");

  if (state.pollTimer) clearInterval(state.pollTimer);
  if (data.is_live && data.refresh_interval_seconds) {
    state.pollTimer = setInterval(() => refresh().catch(() => {}), data.refresh_interval_seconds * 1000);
  }
}

async function refresh() {
  const data = await fetchMap();
  renderAll(data);
  toast("تم التحديث");
}

$("refreshBtn").addEventListener("click", () => refresh().catch((e) => toast(e.message)));
loadConfig();
refresh().catch((e) => toast(e.message));
