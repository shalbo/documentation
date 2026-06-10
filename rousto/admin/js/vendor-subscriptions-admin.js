const STORAGE_KEY = "rousto_admin_config";

const state = { apiBase: "http://localhost:8000", adminKey: "rousto_admin_dev", vendors: [], tiers: [] };

const $ = (sel) => document.querySelector(sel);

const TIER_CLASS = {
  standard: "tier-standard",
  professional: "tier-professional",
  enterprise: "tier-enterprise",
};

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
  setTimeout(() => el.classList.remove("show"), 3200);
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
    const msg = body?.detail?.message || body?.error?.message || `خطأ ${res.status}`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return body;
}

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("ar-LY");
}

function tierPill(tier) {
  if (!tier) return "—";
  const cls = TIER_CLASS[tier.slug] || "tier-standard";
  return `<span class="tier-pill ${cls}">${tier.name_ar}</span>`;
}

function renderTable() {
  const tbody = $("#vendorsTable tbody");
  $("#vendorCount").textContent = String(state.vendors.length);
  if (!state.vendors.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">لا يوجد تجار</td></tr>';
    return;
  }
  tbody.innerHTML = state.vendors
    .map((v) => {
      const sub = v.subscription;
      const limit = v.tier?.is_unlimited_products
        ? "∞"
        : `${v.products_count}/${v.tier?.products_limit ?? "—"}`;
      return `<tr>
        <td><b>${v.business_name}</b><br><small>${v.email}</small></td>
        <td>${tierPill(v.tier)}</td>
        <td>${limit}</td>
        <td>${formatDate(sub?.expires_at)}</td>
        <td>${v.status}</td>
        <td><button class="btn btn-secondary" data-edit-vendor="${v.vendor_id}">تغيير الباقة</button></td>
      </tr>`;
    })
    .join("");
}

function fillTierSelect() {
  const sel = $("#modalTierId");
  sel.innerHTML = state.tiers
    .filter((t) => t.is_active && ["standard", "professional", "enterprise"].includes(t.slug))
    .map((t) => `<option value="${t.id}">${t.name_ar} (${t.slug})</option>`)
    .join("");
}

async function loadAll() {
  try {
    const [vendorsRes, tiersRes] = await Promise.all([
      api("/admin/vendor-subscriptions"),
      api("/admin/tiers"),
    ]);
    state.vendors = vendorsRes.data || [];
    state.tiers = tiersRes.data || [];
    renderTable();
    fillTierSelect();
  } catch (err) {
    toast(err.message, true);
  }
}

function openModal(vendorId) {
  const vendor = state.vendors.find((v) => v.vendor_id === vendorId);
  if (!vendor) return;
  $("#modalVendorId").value = vendorId;
  $("#modalVendorName").textContent = vendor.business_name;
  if (vendor.tier?.id) $("#modalTierId").value = vendor.tier.id;
  $("#modalExpires").value = "";
  $("#modalNote").value = "";
  $("#modal").classList.add("show");
}

async function saveModal() {
  const vendorId = $("#modalVendorId").value;
  const tierId = $("#modalTierId").value;
  const expires = $("#modalExpires").value;
  const payload = {
    tier_id: tierId,
    payment_method: $("#modalPayment").value,
    payment_note: $("#modalNote").value.trim() || null,
  };
  if (expires) payload.expires_at = new Date(expires).toISOString();

  try {
    const body = await api(`/admin/vendors/${vendorId}/subscription`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
    $("#modal").classList.remove("show");
    toast(body.meta?.message || "تم تحديث الاشتراك");
    loadAll();
  } catch (err) {
    toast(err.message, true);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadConfig();
  loadAll();
  $("#refreshBtn").addEventListener("click", loadAll);
  $("#vendorsTable").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-edit-vendor]");
    if (btn) openModal(btn.dataset.editVendor);
  });
  $("#modalSave").addEventListener("click", saveModal);
  $("#modalCancel").addEventListener("click", () => $("#modal").classList.remove("show"));
  $("#modal").addEventListener("click", (e) => {
    if (e.target.id === "modal") $("#modal").classList.remove("show");
  });
});
