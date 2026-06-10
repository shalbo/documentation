const VENDOR_STORAGE_KEY = "rousto_vendor_config";
const ADMIN_STORAGE_KEY = "rousto_admin_config";

function loadStoredConfig(key) {
  try {
    return JSON.parse(localStorage.getItem(key) || "{}");
  } catch (_) {
    return {};
  }
}

function saveStoredConfig(key, data) {
  localStorage.setItem(key, JSON.stringify(data));
}

function toast(msg, isError = false) {
  const el = document.querySelector("#toast");
  if (!el) return;
  el.textContent = msg;
  el.className = "toast show" + (isError ? " error" : "");
  setTimeout(() => el.classList.remove("show"), 2800);
}

async function fetchApi(apiBase, path, options = {}) {
  const res = await fetch(`${apiBase.replace(/\/$/, "")}/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(body?.error?.message || `خطأ ${res.status}`);
  }
  return body;
}

function normalizePoint(lat, lng) {
  return { lat: Number(lat), lng: Number(lng) };
}

function collectMapPoints(payload) {
  const points = [];
  if (payload.base_location?.lat != null) {
    points.push({
      type: "base",
      label: "القاعدة",
      ...normalizePoint(payload.base_location.lat, payload.base_location.lng),
    });
  }
  if (payload.live_location?.lat != null) {
    points.push({
      type: "live",
      label: "الموقع المباشر",
      ...normalizePoint(payload.live_location.lat, payload.live_location.lng),
    });
  }
  if (payload.active_job?.destination?.lat != null) {
    points.push({
      type: "destination",
      label: payload.active_job.destination.label || "العميل",
      ...normalizePoint(
        payload.active_job.destination.lat,
        payload.active_job.destination.lng
      ),
    });
  }
  (payload.trail || []).forEach((p, i) => {
    points.push({
      type: "trail",
      label: `مسار ${i + 1}`,
      ...normalizePoint(p.lat, p.lng),
    });
  });
  return points;
}

function pointStyle(type) {
  const styles = {
    base: { color: "#5B5E66", icon: "🏠" },
    live: { color: "#E11B22", icon: "🚐" },
    destination: { color: "#15161A", icon: "📍" },
    trail: { color: "#1E9E6A", icon: "·" },
  };
  return styles[type] || styles.trail;
}

function renderRelativeMap(container, payload) {
  const points = collectMapPoints(payload);
  if (!points.length) {
    container.innerHTML = '<div class="map-empty">لا توجد إحداثيات</div>';
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
      const style = pointStyle(p.type);
      const left = normX(p.lng).toFixed(1);
      const top = normY(p.lat).toFixed(1);
      const size = p.type === "trail" ? 10 : 28;
      return `<div class="map-marker map-marker-${p.type}" style="left:calc(${left}% - ${size / 2}px);top:calc(${top}% - ${size / 2}px);background:${style.color}" title="${p.label}">${p.type === "trail" ? "" : style.icon}</div>`;
    })
    .join("");

  container.innerHTML = `
    <div class="map-canvas">
      <div class="map-road"></div>
      ${markers}
    </div>
  `;
}

function renderMultiVendorMap(container, vendors) {
  const points = [];
  vendors.forEach((v) => {
    if (v.live_location?.lat != null) {
      points.push({
        type: "live",
        label: v.business_name,
        vendor: v,
        ...normalizePoint(v.live_location.lat, v.live_location.lng),
      });
    } else if (v.base_location?.lat != null) {
      points.push({
        type: "base",
        label: v.business_name,
        vendor: v,
        ...normalizePoint(v.base_location.lat, v.base_location.lng),
      });
    }
  });

  if (!points.length) {
    container.innerHTML = '<div class="map-empty">لا يوجد فنيون على الخريطة</div>';
    return;
  }

  const lats = points.map((p) => p.lat);
  const lngs = points.map((p) => p.lng);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);
  const latSpan = Math.max(maxLat - minLat, 0.001);
  const lngSpan = Math.max(maxLng - minLng, 0.001);
  const normX = (lng) => ((lng - minLng) / lngSpan) * 100;
  const normY = (lat) => 100 - ((lat - minLat) / latSpan) * 100;

  const markers = points
    .map((p) => {
      const left = normX(p.lng).toFixed(1);
      const top = normY(p.lat).toFixed(1);
      const avail = p.vendor.is_available ? "متاح" : "غير متاح";
      return `<div class="map-marker map-marker-live" style="left:calc(${left}% - 14px);top:calc(${top}% - 14px)" title="${p.label} · ${avail}">
        <span class="map-marker-label">${p.label}</span>
      </div>`;
    })
    .join("");

  container.innerHTML = `<div class="map-canvas map-canvas-wide"><div class="map-road"></div>${markers}</div>`;
}

function formatJobSummary(job) {
  if (!job) return "لا توجد مهمة نشطة";
  const parts = [
    job.reference,
    job.status,
    job.destination?.label || "",
  ];
  if (job.distance_km != null) parts.push(`${job.distance_km} كم`);
  if (job.eta_minutes != null) parts.push(`${job.eta_minutes} د`);
  return parts.filter(Boolean).join(" · ");
}
