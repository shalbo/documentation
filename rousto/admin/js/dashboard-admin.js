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

function statCard(label, value, hint) {
  return `<div class="stat-card"><span class="stat-label">${label}</span><strong class="stat-value">${value}</strong>${hint ? `<span class="stat-hint">${hint}</span>` : ""}</div>`;
}

async function refresh() {
  try {
    const { data } = await api("/admin/marketplace/analytics");
    $("statsGrid").innerHTML = [
      statCard("قطع نشطة", data.active_parts, "في الكتالوج"),
      statCard("وحدات المخزون", data.inventory_units, "جاهزة للبيع"),
      statCard("محلات بمخزون", data.vendors_with_stock, "موزّعون"),
      statCard("مخزون منخفض", data.low_stock_skus, "≤ 5 وحدات"),
      statCard("قطع مباعة", data.parts_sold_total, "إجمالي"),
      statCard("مطالبات ضمان", data.open_warranty_claims, "مفتوحة"),
    ].join("");
    toast("تم تحديث إحصائيات السوق");
  } catch (e) {
    toast(e.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    const { apiBase, adminKey } = JSON.parse(saved);
    if (apiBase) $("apiBase").value = apiBase;
    if (adminKey) $("adminKey").value = adminKey;
  }
  $("refreshBtn").addEventListener("click", refresh);
});
