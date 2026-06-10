const STORAGE_KEY = "rousto_admin_config";

const state = { apiBase: "http://localhost:8000", adminKey: "rousto_admin_dev" };

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
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase: state.apiBase, adminKey: state.adminKey }));
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
  if (!res.ok) {
    throw new Error(body?.error?.message || `خطأ ${res.status}`);
  }
  return body;
}

function renderAnalytics(data) {
  const grid = $("#analyticsGrid");
  const items = [
    ["حملات", data.campaigns_total],
    ["بانرات نشطة", data.banners_active],
    ["شركاء", data.partners_active],
    ["مشتركو نشرة", data.newsletter_subscribers],
    ["إحالات", data.referrals_active],
    ["أحداث UTM", data.attribution_events],
    ["عروض نشطة", data.promotions_active],
    ["آراء منشورة", data.testimonials_published],
  ];
  grid.innerHTML = items
    .map(([label, val]) => `<div><b>${val}</b><div style="color:#888;font-size:.85rem">${label}</div></div>`)
    .join("");
}

function renderTable(tbody, rows, emptyCols) {
  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="${emptyCols}" class="empty">لا توجد بيانات</td></tr>`;
    return;
  }
  tbody.innerHTML = rows.join("");
}

async function refresh() {
  try {
    const [analytics, campaigns, banners, partners, promos, newsletter] = await Promise.all([
      api("/admin/marketing/analytics"),
      api("/admin/marketing/campaigns"),
      api("/admin/marketing/banners"),
      api("/admin/marketing/partners"),
      api("/admin/promotions"),
      api("/admin/marketing/newsletter"),
    ]);

    renderAnalytics(analytics.data);
    renderTable(
      $("#campaignsTable tbody"),
      campaigns.data.map(
        (c) =>
          `<tr><td><b>${c.name_ar}</b><br><small>${c.slug}</small></td><td>${c.channel}</td><td>${c.is_active ? "نشط" : "معطّل"}</td></tr>`
      ),
      3
    );
    renderTable(
      $("#bannersTable tbody"),
      banners.data.map(
        (b) =>
          `<tr><td>${b.title_ar}</td><td>${b.placement}</td><td>${b.is_active !== false ? "نشط" : "معطّل"}</td></tr>`
      ),
      3
    );
    renderTable(
      $("#partnersTable tbody"),
      partners.data.map((p) => `<tr><td>${p.name_ar}</td><td>${p.sort_order}</td></tr>`),
      2
    );
    renderTable(
      $("#promotionsTable tbody"),
      promos.data.map(
        (p) =>
          `<tr><td><b>${p.code}</b></td><td>${p.title_ar}</td><td>${p.is_active ? "نشط" : "معطّل"}</td></tr>`
      ),
      3
    );
    renderTable(
      $("#newsletterTable tbody"),
      newsletter.data.map(
        (s) => `<tr><td>${s.email}</td><td>${s.source}</td><td>${s.subscribed_at.slice(0, 10)}</td></tr>`
      ),
      3
    );
    toast("تم تحديث بيانات التسويق");
  } catch (err) {
    toast(err.message, true);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadConfig();
  $("#connectBtn").addEventListener("click", refresh);
});
