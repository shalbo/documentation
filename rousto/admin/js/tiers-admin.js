const STORAGE_KEY = "rousto_admin_config";

const state = {
  apiBase: "http://localhost:8000",
  adminKey: "rousto_admin_dev",
  tiers: [],
  editingId: null,
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
    const msg =
      body?.detail?.message ||
      body?.error?.message ||
      body?.detail ||
      `خطأ ${res.status}`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return body;
}

function formatPrice(price) {
  if (!price) return "مجاني";
  return `${Number(price).toLocaleString("ar-LY")} د.ل`;
}

function limitLabel(limit) {
  return limit === -1 ? "غير محدود ∞" : `${limit} قطعة`;
}

function toggleHtml(id, field, label, hint, checked) {
  return `<label class="toggle-row">
    <span>${label}<small>${hint}</small></span>
    <div class="switch">
      <input type="checkbox" id="${id}-${field}" data-tier-field="${field}" ${checked ? "checked" : ""} />
      <span class="slider"></span>
    </div>
  </label>`;
}

function renderTierCard(tier) {
  const isGold = tier.has_gold_badge;
  const editing = state.editingId === tier.id;
  return `<article class="tier-card ${isGold ? "gold" : ""} ${editing ? "editing" : ""}" data-tier-id="${tier.id}">
    <div class="tier-head">
      <div>
        <div class="tier-name">${tier.name_ar}</div>
        <div class="tier-slug">${tier.slug} · ${tier.name_en}</div>
      </div>
      <div>
        ${isGold ? '<span class="badge-gold">ذهبي</span>' : ""}
        <div class="tier-price">${formatPrice(tier.price)}</div>
      </div>
    </div>
    <div class="tier-body">
      <div class="name-fields">
        <div>
          <label for="${tier.id}-name_ar">الاسم بالعربية</label>
          <input id="${tier.id}-name_ar" data-tier-field="name_ar" value="${tier.name_ar}" />
        </div>
        <div>
          <label for="${tier.id}-name_en">الاسم بالإنجليزية</label>
          <input id="${tier.id}-name_en" data-tier-field="name_en" value="${tier.name_en}" />
        </div>
      </div>
      <div class="tier-limit">
        <div style="flex:1">
          <label for="${tier.id}-price">السعر الشهري</label>
          <input id="${tier.id}-price" type="number" min="0" step="0.01" data-tier-field="price" value="${tier.price}" />
        </div>
        <div style="flex:1">
          <label for="${tier.id}-products_limit">سقف القطع</label>
          <input id="${tier.id}-products_limit" type="number" min="-1" step="1" data-tier-field="products_limit" value="${tier.products_limit}" />
          <small>-1 = غير محدود · الحالي: ${limitLabel(tier.products_limit)}</small>
        </div>
      </div>
      <div class="feature-toggles">
        ${toggleHtml(tier.id, "allow_excel_upload", "رفع Excel", "الرفع الجماعي لقطع الغيار", tier.allow_excel_upload)}
        ${toggleHtml(tier.id, "allow_vin_decoder", "فك ترميز VIN", "ربط القطع برقم الهيكل", tier.allow_vin_decoder)}
        ${toggleHtml(tier.id, "allow_unlimited_chat", "محادثة غير محدودة", "دردشة العملاء بدون حد", tier.allow_unlimited_chat)}
        ${toggleHtml(tier.id, "has_gold_badge", "شارة ذهبية", "تمييز المحل في السوق", tier.has_gold_badge)}
      </div>
    </div>
    <div class="tier-foot">
      <div class="tier-meta">
        <b>${tier.vendor_count ?? 0}</b> تاجر مرتبط
        ${tier.is_unlimited_products ? " · مخزون ∞" : ""}
      </div>
      <button class="btn btn-primary" data-save-tier="${tier.id}">حفظ التعديلات</button>
    </div>
  </article>`;
}

function renderTiers() {
  const grid = $("#tierGrid");
  if (!state.tiers.length) {
    grid.innerHTML = '<div class="empty-tiers">لا توجد باقات</div>';
    return;
  }
  grid.innerHTML = state.tiers.map(renderTierCard).join("");
}

function collectTierPayload(tierId) {
  const card = document.querySelector(`[data-tier-id="${tierId}"]`);
  if (!card) return null;

  const getVal = (field) => {
    const el = card.querySelector(`[data-tier-field="${field}"]`);
    if (!el) return undefined;
    if (el.type === "checkbox") return el.checked;
    if (el.type === "number") return Number(el.value);
    return el.value.trim();
  };

  return {
    name_ar: getVal("name_ar"),
    name_en: getVal("name_en"),
    price: getVal("price"),
    products_limit: getVal("products_limit"),
    allow_excel_upload: getVal("allow_excel_upload"),
    allow_vin_decoder: getVal("allow_vin_decoder"),
    allow_unlimited_chat: getVal("allow_unlimited_chat"),
    has_gold_badge: getVal("has_gold_badge"),
  };
}

async function loadTiers() {
  try {
    const body = await api("/admin/tiers");
    state.tiers = body.data || [];
    renderTiers();
  } catch (err) {
    toast(err.message, true);
    $("#tierGrid").innerHTML = `<div class="empty-tiers">${err.message}</div>`;
  }
}

async function saveTier(tierId) {
  const payload = collectTierPayload(tierId);
  if (!payload) return;

  if (payload.products_limit < -1) {
    toast("سقف القطع: استخدم -1 للغير محدود أو عدداً موجباً", true);
    return;
  }
  if (payload.price < 0) {
    toast("السعر لا يمكن أن يكون سالباً", true);
    return;
  }

  state.editingId = tierId;
  renderTiers();

  try {
    const body = await api(`/admin/tiers/${tierId}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    const idx = state.tiers.findIndex((t) => t.id === tierId);
    if (idx >= 0) state.tiers[idx] = body.data;
    state.editingId = null;
    renderTiers();
    toast(body.meta?.message || "تم تحديث قيود الباقة بنجاح");
  } catch (err) {
    state.editingId = null;
    renderTiers();
    toast(err.message, true);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadConfig();
  loadTiers();

  $("#refreshBtn").addEventListener("click", loadTiers);
  $("#apiBase").addEventListener("change", saveConfig);
  $("#adminKey").addEventListener("change", saveConfig);

  $("#tierGrid").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-save-tier]");
    if (btn) saveTier(btn.dataset.saveTier);
  });
});
