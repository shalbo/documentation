const KEY = "rousto_admin_config";
const state = { apiBase: "http://localhost:8000", adminKey: "rousto_admin_dev", withdrawals: [] };
const $ = (s) => document.querySelector(s);

function cfg() {
  try {
    const s = JSON.parse(localStorage.getItem(KEY) || "{}");
    if (s.apiBase) state.apiBase = s.apiBase;
    if (s.adminKey) state.adminKey = s.adminKey;
  } catch (_) {}
  $("#apiBase").value = state.apiBase;
  $("#adminKey").value = state.adminKey;
}

async function api(path, opts = {}) {
  state.apiBase = $("#apiBase").value.replace(/\/$/, "");
  state.adminKey = $("#adminKey").value.trim();
  localStorage.setItem(KEY, JSON.stringify({ apiBase: state.apiBase, adminKey: state.adminKey }));
  const res = await fetch(`${state.apiBase}/api/v1${path}`, {
    ...opts,
    headers: { "Content-Type": "application/json", "X-Admin-Key": state.adminKey, ...(opts.headers || {}) },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.detail?.message || `خطأ ${res.status}`);
  return body;
}

function toast(m, err) {
  const el = $("#toast");
  el.textContent = m;
  el.className = "toast show" + (err ? " error" : "");
  setTimeout(() => el.classList.remove("show"), 2800);
}

function renderOverview(d) {
  $("#overview").innerHTML = `
    <div class="ov-card highlight"><span>عمولات المنصة</span><b>${Number(d.platform_commission_lyd).toFixed(2)} د.ل</b></div>
    <div class="ov-card"><span>طلبات سحب معلّقة</span><b>${d.pending_withdrawals_count}</b></div>
    <div class="ov-card"><span>قيمة السحب المعلّقة</span><b>${Number(d.pending_withdrawals_lyd).toFixed(2)} د.ل</b></div>
  `;
}

function renderWithdrawals(rows) {
  state.withdrawals = rows;
  const tbody = $("#withdrawTable tbody");
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">لا توجد طلبات</td></tr>';
    return;
  }
  tbody.innerHTML = rows.map((r) => `
    <tr>
      <td><small>${r.vendor_id}</small></td>
      <td><b>${r.amount_lyd} د.ل</b></td>
      <td>${r.iban || "—"}</td>
      <td>${r.status}</td>
      <td>
        ${r.status === "pending" ? `<button class="btn btn-primary" data-pay="${r.id}">اعتماد وتحويل</button>` : "—"}
      </td>
    </tr>`).join("");
}

function renderAudit(rows) {
  $("#auditList").innerHTML = rows.length
    ? rows.map((r) => `<div style="padding:6px 0;border-bottom:1px solid var(--line);font-size:.85rem"><b>${r.event_type}</b> · ${r.gateway || "—"} · ${r.created_at || ""}</div>`).join("")
    : '<div class="empty">—</div>';
}

async function load() {
  try {
    const [ov, wd, audit] = await Promise.all([
      api("/admin/payments/overview"),
      api("/admin/withdrawals?status=pending"),
      api("/admin/payments/audit?limit=30"),
    ]);
    renderOverview(ov.data);
    renderWithdrawals(wd.data);
    renderAudit(audit.data);
  } catch (e) {
    toast(e.message, true);
  }
}

async function markPaid(id) {
  try {
    const body = await api(`/admin/withdrawals/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ mark_paid: true, admin_note: "تحويل مصرفي مكتمل" }),
    });
    toast(body.meta?.message || "تم التحويل");
    load();
  } catch (e) {
    toast(e.message, true);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  cfg();
  load();
  $("#refreshBtn").onclick = load;
  $("#withdrawTable").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-pay]");
    if (btn) markPaid(btn.dataset.pay);
  });
});
