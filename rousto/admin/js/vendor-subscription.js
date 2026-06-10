const STORAGE_KEY = "rousto_vendor_config";

const state = { apiBase: "http://localhost:8000", vendorId: "", data: null };

const $ = (sel) => document.querySelector(sel);

function loadConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    if (saved.apiBase) state.apiBase = saved.apiBase;
    if (saved.vendorId) state.vendorId = saved.vendorId;
  } catch (_) {}
  $("#apiBase").value = state.apiBase;
  $("#vendorId").value = state.vendorId || "v0000000-0000-4000-8000-000000000001";
}

function saveConfig() {
  state.apiBase = $("#apiBase").value.replace(/\/$/, "");
  state.vendorId = $("#vendorId").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
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
      "X-Vendor-Id": state.vendorId,
      ...(options.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = body?.detail?.message || body?.error?.message || `خطأ ${res.status}`;
    throw new Error(msg);
  }
  return body;
}

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("ar-LY", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function renderCurrent() {
  const d = state.data;
  if (!d) return;
  const tier = d.current_tier;
  const sub = d.subscription;
  const usage = d.usage;
  $("#currentTierName").textContent = tier.name_ar;
  $("#expiryLine").textContent = sub?.expires_at
    ? `تنتهي باقتك في: ${formatDate(sub.expires_at)}`
    : "لا يوجد تاريخ انتهاء مسجّل";
  $("#usedCount").textContent = String(usage.products_count);
  $("#limitCount").textContent = usage.is_unlimited_products ? "∞" : String(usage.products_limit);
  $("#remainCount").textContent = usage.is_unlimited_products
    ? "∞"
    : String(usage.products_remaining ?? 0);
}

function planFeatures(tier) {
  const feats = [];
  feats.push(
    usageLabel(tier.products_limit)
  );
  if (tier.allow_excel_upload) feats.push("رفع Excel / ZIP");
  if (tier.allow_vin_decoder) feats.push("فك ترميز VIN");
  if (tier.allow_unlimited_chat) feats.push("محادثة غير محدودة");
  if (tier.has_gold_badge) feats.push("شارة VIP ذهبية");
  return feats.map((f) => `<div class="feat">✓ ${f}</div>`).join("");
}

function usageLabel(limit) {
  return limit === -1 ? "قطع غير محدودة" : `حتى ${limit} قطعة`;
}

function renderPlans() {
  const grid = $("#planGrid");
  const d = state.data;
  if (!d?.available_tiers?.length) {
    grid.innerHTML = '<div class="empty">لا توجد باقات</div>';
    return;
  }
  const currentSlug = d.current_tier.slug;
  grid.innerHTML = d.available_tiers
    .map((tier) => {
      const isCurrent = tier.slug === currentSlug;
      const isEnterprise = tier.slug === "enterprise";
      const canUpgrade = tier.sort_order > d.current_tier.sort_order;
      return `<article class="plan-card ${isCurrent ? "current" : ""} ${isEnterprise ? "enterprise" : ""}">
        <div class="plan-head">
          ${isEnterprise ? '<span class="vip-badge">VIP · باقة الشركات</span>' : ""}
          <div class="plan-name">${tier.name_ar}</div>
          <div class="plan-price">${tier.price ? tier.price + " د.ل / شهر" : "مجاني"}</div>
        </div>
        <div class="plan-body">${planFeatures(tier)}</div>
        <div class="plan-foot">
          ${
            isCurrent
              ? '<span class="current-pill">باقتك الحالية</span>'
              : `<button class="btn-upgrade" data-upgrade="${tier.id}" ${canUpgrade ? "" : "disabled"}>${
                  canUpgrade ? "طلب ترقية" : "أقل من باقتك"
                }</button>`
          }
        </div>
      </article>`;
    })
    .join("");
}

async function load() {
  try {
    const body = await api("/vendor/subscription");
    state.data = body.data;
    renderCurrent();
    renderPlans();
  } catch (err) {
    toast(err.message, true);
  }
}

async function requestUpgrade(tierId) {
  try {
    const body = await api("/vendor/subscription/upgrade-request", {
      method: "POST",
      body: JSON.stringify({ tier_id: tierId }),
    });
    toast(body.meta?.message || "تم إرسال طلب الترقية");
  } catch (err) {
    toast(err.message, true);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadConfig();
  load();
  $("#refreshBtn").addEventListener("click", load);
  $("#planGrid").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-upgrade]");
    if (btn) requestUpgrade(btn.dataset.upgrade);
  });
});
