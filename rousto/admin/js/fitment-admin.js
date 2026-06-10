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

async function api(path, opts = {}) {
  const { apiBase, adminKey } = cfg();
  const res = await fetch(`${apiBase}/api/v1${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Key": adminKey,
      ...(opts.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.error?.message || `خطأ ${res.status}`);
  return body;
}

async function refresh() {
  try {
    const makes = await fetch(`${cfg().apiBase}/api/v1/fitment/makes`).then((r) => r.json());
    $("makesBody").innerHTML = makes.data.length
      ? makes.data.map((m) => `<tr><td>${m.name_ar || m.name}</td><td><code>${m.slug}</code></td><td><small>${m.id}</small></td></tr>`).join("")
      : '<tr><td colspan="3" class="empty">لا بيانات</td></tr>';
    toast(`تم تحميل ${makes.data.length} ماركة`);
  } catch (e) {
    toast(e.message);
  }
}

async function loadCompat(partId) {
  const { data } = await api(`/admin/parts/${partId}/compatibilities`);
  $("compatBody").innerHTML = data.length
    ? data.map((c) => {
        const f = c.fitment || {};
        return `<tr>
          <td>${f.year || "—"}</td>
          <td>${f.model?.name || "—"}</td>
          <td>${f.make?.name || "—"}</td>
          <td>${c.fitment_note_ar || "—"}</td>
        </tr>`;
      }).join("")
    : '<tr><td colspan="4" class="empty">لا توافقات</td></tr>';
}

$("refreshBtn").addEventListener("click", refresh);
$("lookupBtn").addEventListener("click", async () => {
  const id = $("lookupPartId").value.trim();
  if (!id) return;
  try {
    await loadCompat(id);
  } catch (e) {
    toast(e.message);
  }
});

$("compatForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const partId = $("partId").value.trim();
  const carYearId = $("carYearId").value.trim();
  try {
    await api(`/admin/parts/${partId}/compatibilities`, {
      method: "POST",
      body: JSON.stringify({ car_year_id: carYearId }),
    });
    toast("تم ربط التوافق");
    await loadCompat(partId);
  } catch (err) {
    toast(err.message);
  }
});

try {
  const s = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  if (s.apiBase) $("apiBase").value = s.apiBase;
  if (s.adminKey) $("adminKey").value = s.adminKey;
} catch (_) {}
refresh();
