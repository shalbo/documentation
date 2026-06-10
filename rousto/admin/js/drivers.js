const STORAGE_KEY = "rousto_admin_config";
const $ = (id) => document.getElementById(id);

function toast(msg, isError) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast show" + (isError ? " error" : "");
  setTimeout(() => el.classList.remove("show"), 2600);
}

function cfg() {
  const apiBase = $("apiBase").value.replace(/\/$/, "");
  const adminKey = $("adminKey").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase, adminKey }));
  return { apiBase, adminKey };
}

async function api(path) {
  const { apiBase, adminKey } = cfg();
  const res = await fetch(`${apiBase}/api/v1${path}`, {
    headers: { "X-Admin-Key": adminKey },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.error?.message || `خطأ ${res.status}`);
  return body;
}

async function patchAvailability(id, isAvailable) {
  const { apiBase, adminKey } = cfg();
  const res = await fetch(`${apiBase}/api/v1/admin/drivers/${id}/availability`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Key": adminKey,
    },
    body: JSON.stringify({ is_available: isAvailable }),
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.error?.message || "فشل التحديث");
}

function renderAnalytics(data) {
  const items = [
    ["إجمالي السائقين", data.drivers_total],
    ["متاحون", data.drivers_available],
    ["مهام معلّقة", data.pending_tow_jobs],
    ["إرسالات نشطة", data.active_dispatches],
  ];
  $("analyticsGrid").innerHTML = items
    .map(([l, v]) => `<div><b>${v}</b><div style="color:#888;font-size:.85rem">${l}</div></div>`)
    .join("");
}

function renderDrivers(rows) {
  const tbody = $("driversBody");
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty">لا سائقين</td></tr>';
    return;
  }
  tbody.innerHTML = rows
    .map(
      (d) => `
      <tr>
        <td><b>${d.full_name}</b><br><small>${d.phone}</small></td>
        <td><span class="type-${d.driver_type}">${d.driver_type}</span></td>
        <td>${d.rating}</td>
        <td>${d.is_available ? "✓" : "—"}</td>
        <td>${d.active_jobs}</td>
        <td>${d.completed_jobs}</td>
        <td>
          <button class="btn btn-sm btn-ghost" data-id="${d.id}" data-available="${!d.is_available}">
            ${d.is_available ? "تعطيل" : "تفعيل"}
          </button>
        </td>
      </tr>`
    )
    .join("");

  tbody.querySelectorAll("button[data-id]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      try {
        await patchAvailability(btn.dataset.id, btn.dataset.available === "true");
        toast("تم التحديث");
        refresh();
      } catch (e) {
        toast(e.message, true);
      }
    });
  });
}

async function refresh() {
  try {
    const type = $("typeFilter").value;
    const q = type ? `?driver_type=${type}` : "";
    const [analytics, drivers] = await Promise.all([
      api("/admin/drivers/analytics"),
      api(`/admin/drivers${q}`),
    ]);
    renderAnalytics(analytics.data);
    renderDrivers(drivers.data);
    toast("تم التحديث");
  } catch (e) {
    toast(e.message, true);
  }
}

$("refreshBtn").addEventListener("click", refresh);
$("typeFilter").addEventListener("change", refresh);

try {
  const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  if (saved.apiBase) $("apiBase").value = saved.apiBase;
  if (saved.adminKey) $("adminKey").value = saved.adminKey;
} catch (_) {}

refresh();
