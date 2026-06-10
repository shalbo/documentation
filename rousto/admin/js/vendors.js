const STORAGE_KEY = "rousto_admin_config";

const state = {
  apiBase: "http://localhost:8000",
  adminKey: "rousto_admin_dev",
  vendors: [],
  statusFilter: "pending",
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
  if (!res.ok) {
    const msg = body?.error?.message || `خطأ ${res.status}`;
    throw new Error(msg);
  }
  return body;
}

async function publicApi(path, options = {}) {
  saveConfig();
  const res = await fetch(`${state.apiBase}/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = body?.error?.message || `خطأ ${res.status}`;
    throw new Error(msg);
  }
  return body;
}

function statusBadge(status) {
  const map = {
    pending: ["badge-warn", "معلّق"],
    approved: ["badge-on", "مُوافَق"],
    rejected: ["badge-off", "مرفوض"],
    suspended: ["badge-off", "موقوف"],
    draft: ["badge-off", "مسودة"],
  };
  const [cls, label] = map[status] || ["badge-off", status];
  return `<span class="badge ${cls}">${label}</span>`;
}

function renderVendors() {
  const tbody = $("#vendorsTable tbody");
  if (!state.vendors.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">لا توجد طلبات</td></tr>';
    return;
  }

  tbody.innerHTML = state.vendors
    .map((v) => {
      const iban = v.bank_account?.iban_masked || "—";
      const actions =
        v.status === "pending"
          ? `<button class="btn btn-primary" data-approve="${v.id}">موافقة</button>
             <button class="btn btn-ghost" data-reject="${v.id}">رفض</button>`
          : v.technician_id
            ? `<small>فني: ${v.technician_id.slice(0, 8)}…</small>`
            : "—";

      return `<tr>
        <td><b>${v.business_name}</b><br><small>${v.city}</small></td>
        <td>${v.contact_name}<br><small>${v.email}</small></td>
        <td>${v.phone}</td>
        <td>${statusBadge(v.status)}</td>
        <td>${iban}</td>
        <td class="actions">${actions}</td>
      </tr>`;
    })
    .join("");
}

async function loadVendors() {
  const q = state.statusFilter ? `?status=${state.statusFilter}` : "";
  const body = await api(`/admin/vendors${q}`);
  state.vendors = body.data || [];
  renderVendors();
  toast(`تم تحميل ${state.vendors.length} طلب`);
}

async function approveVendor(id) {
  if (!confirm("تأكيد الموافقة على هذا الطلب؟")) return;
  await api(`/admin/vendors/${id}/approve`, { method: "POST" });
  toast("تمت الموافقة");
  await loadVendors();
}

async function rejectVendor(id) {
  const reason = prompt("سبب الرفض:");
  if (!reason || reason.trim().length < 3) {
    toast("يجب إدخال سبب الرفض", true);
    return;
  }
  await api(`/admin/vendors/${id}/reject`, {
    method: "POST",
    body: JSON.stringify({ reason: reason.trim() }),
  });
  toast("تم الرفض");
  await loadVendors();
}

$("#connectBtn").addEventListener("click", () => {
  loadVendors().catch((e) => toast(e.message, true));
});

$("#statusFilter").addEventListener("change", (e) => {
  state.statusFilter = e.target.value;
  loadVendors().catch((err) => toast(err.message, true));
});

$("#vendorsTable").addEventListener("click", (e) => {
  const approveId = e.target.closest("[data-approve]")?.dataset.approve;
  const rejectId = e.target.closest("[data-reject]")?.dataset.reject;
  if (approveId) approveVendor(approveId).catch((err) => toast(err.message, true));
  if (rejectId) rejectVendor(rejectId).catch((err) => toast(err.message, true));
});

$("#applicationForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    business_name: $("#bizName").value.trim(),
    contact_name: $("#contactName").value.trim(),
    email: $("#email").value.trim(),
    phone: $("#phone").value.trim(),
    city: $("#city").value.trim() || "الرياض",
    bank_name: $("#bankName").value.trim(),
    account_holder: $("#accountHolder").value.trim(),
    iban: $("#iban").value.trim(),
  };
  try {
    await publicApi("/vendors/applications", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    toast("تم إرسال الطلب");
    e.target.reset();
    $("#city").value = "الرياض";
    await loadVendors();
  } catch (err) {
    toast(err.message, true);
  }
});

loadConfig();
