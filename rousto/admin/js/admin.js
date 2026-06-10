const STORAGE_KEY = "rousto_admin_config";

const state = {
  apiBase: "http://localhost:8000",
  adminKey: "rousto_admin_dev",
  categories: [],
  services: [],
  editingServiceId: null,
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

function renderCategories() {
  const tbody = $("#categoriesTable tbody");
  if (!state.categories.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">لا توجد تصنيفات</td></tr>';
    return;
  }
  tbody.innerHTML = state.categories
    .map((c) => {
      const protectedBadge =
        c.slug === "all" ? '<span class="badge badge-protected">محمي</span>' : "";
      const status = c.is_active
        ? '<span class="badge badge-on">نشط</span>'
        : '<span class="badge badge-off">مخفي</span>';
      const toggleBtn =
        c.slug === "all"
          ? ""
          : `<button class="btn btn-ghost" data-toggle-cat="${c.id}" data-active="${!c.is_active}">
              ${c.is_active ? "إخفاء" : "تفعيل"}
            </button>`;
      return `<tr>
        <td><b>${c.name_ar}</b><br><small>${c.slug}</small> ${protectedBadge}</td>
        <td>${c.sort_order}</td>
        <td>${status}</td>
        <td class="actions">${toggleBtn}</td>
      </tr>`;
    })
    .join("");
}

function fillCategorySelect() {
  const select = $("#serviceCategory");
  const options = state.categories.filter((c) => c.slug !== "all" && c.is_active);
  select.innerHTML = options
    .map((c) => `<option value="${c.id}">${c.name_ar}</option>`)
    .join("");
}

function renderServices() {
  const tbody = $("#servicesTable tbody");
  if (!state.services.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">لا توجد خدمات</td></tr>';
    return;
  }
  tbody.innerHTML = state.services
    .map((s) => {
      const status = s.is_active
        ? '<span class="badge badge-on">نشط</span>'
        : '<span class="badge badge-off">مخفي</span>';
      return `<tr>
        <td><b>${s.name_ar}</b><br><small>${s.slug}</small></td>
        <td>${s.category_name_ar}</td>
        <td>${Math.round(s.price_sar)} دينار</td>
        <td>${s.duration_minutes} د</td>
        <td>${status}</td>
        <td class="actions">
          <button class="btn btn-secondary" data-edit-service="${s.id}">تعديل</button>
          <button class="btn btn-ghost" data-toggle-svc="${s.id}" data-active="${!s.is_active}">
            ${s.is_active ? "إخفاء" : "تفعيل"}
          </button>
        </td>
      </tr>`;
    })
    .join("");
}

function clearServiceForm() {
  state.editingServiceId = null;
  $("#serviceFormTitle").textContent = "إضافة خدمة";
  $("#serviceSlug").value = "";
  $("#serviceName").value = "";
  $("#serviceSubtitle").value = "";
  $("#serviceIcon").value = "";
  $("#servicePrice").value = "";
  $("#serviceDuration").value = "";
  $("#serviceSubmit").textContent = "إضافة";
  $("#serviceCancel").style.display = "none";
}

function fillServiceForm(service) {
  state.editingServiceId = service.id;
  $("#serviceFormTitle").textContent = "تعديل خدمة";
  $("#serviceCategory").value = service.category_id;
  $("#serviceSlug").value = service.slug;
  $("#serviceSlug").disabled = true;
  $("#serviceName").value = service.name_ar;
  $("#serviceSubtitle").value = service.subtitle_ar || "";
  $("#serviceIcon").value = service.icon_key || "";
  $("#servicePrice").value = service.price_sar;
  $("#serviceDuration").value = service.duration_minutes;
  $("#serviceSubmit").textContent = "حفظ";
  $("#serviceCancel").style.display = "inline-block";
}

async function refreshAll() {
  const [cats, svcs] = await Promise.all([
    api("/admin/categories"),
    api("/admin/services"),
  ]);
  state.categories = cats.data;
  state.services = svcs.data;
  renderCategories();
  renderServices();
  fillCategorySelect();
}

async function init() {
  loadConfig();
  $("#connectBtn").addEventListener("click", async () => {
    try {
      await refreshAll();
      toast("تم الاتصال وتحميل الكتالوج");
    } catch (e) {
      toast(e.message, true);
    }
  });

  $("#categoryForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      await api("/admin/categories", {
        method: "POST",
        body: JSON.stringify({
          slug: $("#catSlug").value.trim(),
          name_ar: $("#catName").value.trim(),
          sort_order: Number($("#catOrder").value) || 0,
        }),
      });
      $("#catSlug").value = "";
      $("#catName").value = "";
      $("#catOrder").value = "";
      await refreshAll();
      toast("تم إنشاء التصنيف");
    } catch (err) {
      toast(err.message, true);
    }
  });

  $("#serviceForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      category_id: $("#serviceCategory").value,
      slug: $("#serviceSlug").value.trim(),
      name_ar: $("#serviceName").value.trim(),
      subtitle_ar: $("#serviceSubtitle").value.trim() || null,
      icon_key: $("#serviceIcon").value.trim() || null,
      price_sar: Number($("#servicePrice").value),
      duration_minutes: Number($("#serviceDuration").value),
    };
    try {
      const wasEdit = !!state.editingServiceId;
      if (wasEdit) {
        const { slug, category_id, ...updates } = payload;
        await api(`/admin/services/${state.editingServiceId}`, {
          method: "PATCH",
          body: JSON.stringify({
            category_id,
            ...updates,
          }),
        });
      } else {
        await api("/admin/services", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      clearServiceForm();
      $("#serviceSlug").disabled = false;
      await refreshAll();
      toast(wasEdit ? "تم حفظ الخدمة" : "تم إنشاء الخدمة");
    } catch (err) {
      toast(err.message, true);
    }
  });

  $("#serviceCancel").addEventListener("click", () => {
    clearServiceForm();
    $("#serviceSlug").disabled = false;
  });

  $("#categoriesTable").addEventListener("click", async (e) => {
    const btn = e.target.closest("[data-toggle-cat]");
    if (!btn) return;
    try {
      await api(`/admin/categories/${btn.dataset.toggleCat}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: btn.dataset.active === "true" }),
      });
      await refreshAll();
      toast("تم تحديث التصنيف");
    } catch (err) {
      toast(err.message, true);
    }
  });

  $("#servicesTable").addEventListener("click", async (e) => {
    const editBtn = e.target.closest("[data-edit-service]");
    if (editBtn) {
      const service = state.services.find((s) => s.id === editBtn.dataset.editService);
      if (service) fillServiceForm(service);
      return;
    }
    const toggleBtn = e.target.closest("[data-toggle-svc]");
    if (!toggleBtn) return;
    try {
      await api(`/admin/services/${toggleBtn.dataset.toggleSvc}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: toggleBtn.dataset.active === "true" }),
      });
      await refreshAll();
      toast("تم تحديث الخدمة");
    } catch (err) {
      toast(err.message, true);
    }
  });
}

document.addEventListener("DOMContentLoaded", init);
