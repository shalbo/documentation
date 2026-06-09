const STORAGE_KEY = "rousto_admin_config";

const state = {
  apiBase: "http://localhost:8000",
  adminKey: "rousto_admin_dev",
  dispatches: [],
  selectedId: null,
};

const $ = (sel) => document.querySelector(sel);

function loadConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    if (saved.apiBase) state.apiBase = saved.apiBase;
    if (saved.adminKey) state.adminKey = saved.adminKey;
  } catch (_) {}
  $("#apiBase").value = state.apiBase;
  $("#adminKey").value = state.adminKey;
}

function saveConfig() {
  state.apiBase = $("#apiBase").value.replace(/\/$/, "");
  state.adminKey = $("#adminKey").value.trim();
  localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({ apiBase: state.apiBase, adminKey: state.adminKey })
  );
}

function toast(msg, isError = false) {
  const el = $("#toast");
  el.textContent = msg;
  el.className = "toast show" + (isError ? " error" : "");
  setTimeout(() => el.classList.remove("show"), 2800);
}

async function api(path, options = {}) {
  saveConfig();
  const res = await fetch(`${state.apiBase}/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Key": state.adminKey,
      ...(options.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.error?.message || `خطأ ${res.status}`);
  return body;
}

function renderMap(item) {
  const host = $("#mapView");
  if (!item) {
    host.innerHTML = '<div class="map-empty">اختر إرسالاً</div>';
    return;
  }

  const points = [];
  if (item.pickup) points.push({ ...item.pickup, type: "pickup", icon: "⚠️" });
  if (item.dropoff) points.push({ ...item.dropoff, type: "dropoff", icon: "🏭" });
  (item.trail || []).forEach((p) => points.push({ ...p, type: "trail" }));
  if (item.tow_truck?.location) {
    points.push({ ...item.tow_truck.location, type: "truck", icon: "🚛" });
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
      const size = p.type === "trail" ? 8 : 30;
      const bg =
        p.type === "pickup"
          ? "#B07D00"
          : p.type === "dropoff"
            ? "#15161A"
            : p.type === "truck"
              ? "#E11B22"
              : "#1E9E6A";
      return `<div class="map-marker" style="left:calc(${left}% - ${size / 2}px);top:calc(${top}% - ${size / 2}px);width:${size}px;height:${size}px;background:${bg}">${p.icon || ""}</div>`;
    })
    .join("");

  host.innerHTML = `<div class="map-canvas map-canvas-wide"><div class="map-road"></div>${markers}</div>`;
  $("#mapCaption").textContent = `${item.dispatch.reference} · ${item.dispatch.dispatch_phase_label_ar} · ${item.active_leg || "—"}`;
}

function renderTable() {
  const tbody = $("#dispatchTable tbody");
  if (!state.dispatches.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">لا توجد إرسالات</td></tr>';
    return;
  }

  tbody.innerHTML = state.dispatches
    .map((d) => {
      const dispatch = d.dispatch;
      const selected = dispatch.id === state.selectedId ? "selected" : "";
      return `<tr class="${selected}" data-id="${dispatch.id}">
        <td><b>${dispatch.reference}</b></td>
        <td>${d.pickup.label}</td>
        <td>${d.dropoff.label}</td>
        <td><span class="badge badge-warn">${dispatch.status}</span></td>
        <td class="actions">
          <button class="btn btn-ghost" data-view="${dispatch.id}">عرض</button>
          <button class="btn btn-primary" data-advance="${dispatch.id}">تقدّم</button>
        </td>
      </tr>`;
    })
    .join("");
}

async function refresh() {
  const body = await api("/admin/towing/dispatches/map");
  state.dispatches = body.data || [];
  if (!state.selectedId && state.dispatches.length) {
    state.selectedId = state.dispatches[0].dispatch.id;
  }
  renderTable();
  const selected = state.dispatches.find((d) => d.dispatch.id === state.selectedId);
  renderMap(selected || state.dispatches[0]);
  toast(`تم تحميل ${state.dispatches.length} إرسال`);
}

$("#refreshBtn").addEventListener("click", () => {
  refresh().catch((e) => toast(e.message, true));
});

$("#dispatchTable").addEventListener("click", async (e) => {
  const viewId = e.target.closest("[data-view]")?.dataset.view;
  const advanceId = e.target.closest("[data-advance]")?.dataset.advance;
  if (viewId) {
    state.selectedId = viewId;
    renderTable();
    renderMap(state.dispatches.find((d) => d.dispatch.id === viewId));
    return;
  }
  if (advanceId) {
    try {
      await api(`/admin/towing/dispatches/${advanceId}/advance`, { method: "POST" });
      await refresh();
    } catch (err) {
      toast(err.message, true);
    }
  }
});

loadConfig();
refresh().catch(() => {});
