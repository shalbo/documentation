const STORAGE_KEY = "rousto_admin_config";

const state = {
  apiBase: "http://localhost:8000",
  adminKey: "rousto_admin_dev",
  cities: [],
  editingCityId: null,
};

const $ = (sel) => document.querySelector(sel);

const REGION_LABELS = {
  West: "غرب",
  East: "شرق",
  South: "جنوب",
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

function buildQuery() {
  const params = new URLSearchParams();
  const region = $("#filterRegion").value;
  const active = $("#filterActive").value;
  if (region) params.set("region", region);
  if (active !== "") params.set("active", active);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

function renderCities() {
  const tbody = $("#citiesTable tbody");
  $("#cityCount").textContent = String(state.cities.length);
  if (!state.cities.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">لا توجد مدن</td></tr>';
    return;
  }
  tbody.innerHTML = state.cities
    .map((c) => {
      const status = c.is_active
        ? '<span class="badge badge-on">نشطة</span>'
        : '<span class="badge badge-off">معطّلة</span>';
      return `<tr>
        <td><b>${c.name_ar}</b></td>
        <td>${c.name_en}</td>
        <td>${REGION_LABELS[c.region] || c.region}</td>
        <td>${status}</td>
        <td class="actions">
          <button class="btn btn-secondary" data-edit-city="${c.id}">تعديل</button>
          <button class="btn btn-ghost" data-toggle-city="${c.id}" data-active="${!c.is_active}">
            ${c.is_active ? "تعطيل" : "تفعيل"}
          </button>
        </td>
      </tr>`;
    })
    .join("");
}

function resetForm() {
  state.editingCityId = null;
  $("#cityId").value = "";
  $("#cityForm").reset();
  $("#cityFormTitle").textContent = "إضافة مدينة";
  $("#citySubmit").textContent = "إضافة";
  $("#cityCancel").style.display = "none";
}

function fillForm(city) {
  state.editingCityId = city.id;
  $("#cityId").value = city.id;
  $("#nameAr").value = city.name_ar;
  $("#nameEn").value = city.name_en;
  $("#region").value = city.region;
  $("#cityFormTitle").textContent = "تعديل مدينة";
  $("#citySubmit").textContent = "حفظ التعديل";
  $("#cityCancel").style.display = "inline-flex";
}

async function refresh() {
  try {
    const { data } = await api(`/admin/cities${buildQuery()}`);
    state.cities = data;
    renderCities();
    toast(`تم تحميل ${data.length} مدينة`);
  } catch (err) {
    toast(err.message, true);
  }
}

$("#refreshBtn").addEventListener("click", refresh);
$("#filterRegion").addEventListener("change", refresh);
$("#filterActive").addEventListener("change", refresh);

$("#cityCancel").addEventListener("click", resetForm);

$("#cityForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    name_ar: $("#nameAr").value.trim(),
    name_en: $("#nameEn").value.trim(),
    region: $("#region").value,
  };
  try {
    if (state.editingCityId) {
      await api(`/admin/cities/${state.editingCityId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      toast("تم تحديث المدينة");
    } else {
      await api("/admin/cities", {
        method: "POST",
        body: JSON.stringify({ ...payload, is_active: true }),
      });
      toast("تمت إضافة المدينة");
    }
    resetForm();
    refresh();
  } catch (err) {
    toast(err.message, true);
  }
});

$("#citiesTable").addEventListener("click", async (e) => {
  const editBtn = e.target.closest("[data-edit-city]");
  const toggleBtn = e.target.closest("[data-toggle-city]");
  if (editBtn) {
    const city = state.cities.find((c) => c.id === editBtn.dataset.editCity);
    if (city) fillForm(city);
    return;
  }
  if (toggleBtn) {
    const id = toggleBtn.dataset.toggleCity;
    const activate = toggleBtn.dataset.active === "true";
    try {
      await api(`/admin/cities/${id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: activate }),
      });
      toast(activate ? "تم تفعيل المدينة" : "تم تعطيل المدينة");
      refresh();
    } catch (err) {
      toast(err.message, true);
    }
  }
});

loadConfig();
refresh();
