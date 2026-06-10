const STORAGE_KEY = "rousto_admin_config";
const $ = (id) => document.getElementById(id);

function cfg() {
  const apiBase = $("apiBase").value.replace(/\/$/, "");
  const adminKey = $("adminKey").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase, adminKey }));
  return { apiBase, adminKey };
}

function toast(msg) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast show";
  setTimeout(() => el.classList.remove("show"), 2400);
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

async function refresh() {
  try {
    const [parts, claims] = await Promise.all([
      api("/admin/parts"),
      api("/admin/part-warranty-claims"),
    ]);
    const tbody = $("partsBody");
    tbody.innerHTML = parts.data.length
      ? parts.data.map((p) => `
        <tr>
          <td><code>${p.oem_number || p.part_number}</code></td>
          <td>${p.name_ar || p.name}</td>
          <td>${p.vin_prefix || "—"}</td>
          <td>${p.category?.name_ar || p.category?.slug || "—"}</td>
          <td>${p.is_oem ? "✓ OEM" : "—"}</td>
          <td>${p.price_sar} ر.س</td>
        </tr>`).join("")
      : '<tr><td colspan="6" class="empty">لا قطع</td></tr>';

    const cbody = $("claimsBody");
    cbody.innerHTML = claims.data.length
      ? claims.data.map((c) => `
        <tr>
          <td><small>${String(c.user_id).slice(0, 8)}…</small></td>
          <td>${c.description}</td>
          <td>${c.status}</td>
          <td><small>${new Date(c.created_at).toLocaleString("ar-SA")}</small></td>
        </tr>`).join("")
      : '<tr><td colspan="4" class="empty">لا مطالبات</td></tr>';

    toast(`تم تحميل ${parts.data.length} قطعة`);
  } catch (e) {
    toast(e.message);
  }
}

$("refreshBtn").addEventListener("click", refresh);
try {
  const s = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  if (s.apiBase) $("apiBase").value = s.apiBase;
  if (s.adminKey) $("adminKey").value = s.adminKey;
} catch (_) {}
refresh();
