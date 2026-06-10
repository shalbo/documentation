const STORAGE_KEY = 'rousto_vendor_staff_config';

const roleLabels = {
  manager: 'مدير',
  sales: 'مبيعات',
  accountant: 'محاسب',
};

function loadConfig() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
  } catch {
    return {};
  }
}

function saveConfig() {
  const cfg = {
    apiBase: document.getElementById('apiBase').value.trim(),
    vendorId: document.getElementById('vendorId').value.trim(),
    accessToken: document.getElementById('accessToken').value.trim(),
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cfg));
  toast('تم حفظ الإعدادات');
}

function applyConfig() {
  const cfg = loadConfig();
  if (cfg.apiBase) document.getElementById('apiBase').value = cfg.apiBase;
  if (cfg.vendorId) document.getElementById('vendorId').value = cfg.vendorId;
  if (cfg.accessToken) document.getElementById('accessToken').value = cfg.accessToken;
}

function apiClient() {
  const base = document.getElementById('apiBase').value.replace(/\/$/, '');
  const token = document.getElementById('accessToken').value.trim();
  const vendorId = document.getElementById('vendorId').value.trim();
  const headers = { 'Content-Type': 'application/json' };
  if (token) headers.Authorization = `Bearer ${token}`;
  else if (vendorId) headers['X-Vendor-Id'] = vendorId;
  return axios.create({ baseURL: `${base}/api/v1`, headers });
}

function toast(msg, isError = false) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show' + (isError ? ' error' : '');
  setTimeout(() => el.classList.remove('show'), 2800);
}

function renderTable(items) {
  const wrap = document.getElementById('staffTableWrap');
  if (!items.length) {
    wrap.innerHTML = '<p class="empty">لا يوجد موظفون بعد</p>';
    return;
  }
  wrap.innerHTML = `
    <table class="staff-table">
      <thead>
        <tr>
          <th>الاسم</th>
          <th>الهاتف</th>
          <th>الدور</th>
          <th>نشط</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        ${items.map((s) => rowHtml(s)).join('')}
      </tbody>
    </table>`;

  wrap.querySelectorAll('[data-toggle]').forEach((input) => {
    input.addEventListener('change', () => toggleStaff(input.dataset.id, input.checked));
  });
  wrap.querySelectorAll('[data-delete]').forEach((btn) => {
    btn.addEventListener('click', () => deleteStaff(btn.dataset.id));
  });
}

function rowHtml(s) {
  return `<tr>
    <td><strong>${escapeHtml(s.name)}</strong></td>
    <td dir="ltr">${escapeHtml(s.phone)}</td>
    <td><span class="role-badge ${s.role}">${roleLabels[s.role] || s.role}</span></td>
    <td>
      <label class="toggle" title="تفعيل/تعطيل">
        <input type="checkbox" data-toggle data-id="${s.id}" ${s.is_active ? 'checked' : ''} />
        <span></span>
      </label>
    </td>
    <td><button class="btn btn-danger btn-sm" data-delete data-id="${s.id}">حذف</button></td>
  </tr>`;
}

function escapeHtml(t) {
  return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function loadStaff() {
  const wrap = document.getElementById('staffTableWrap');
  wrap.innerHTML = '<p class="empty">جاري التحميل…</p>';
  try {
    const res = await apiClient().get('/vendor/staff');
    const items = res.data?.data || [];
    renderTable(items);
  } catch (e) {
    const msg = e.response?.data?.detail?.message || e.response?.data?.error?.message || e.message;
    wrap.innerHTML = `<p class="empty">${escapeHtml(msg)}</p>`;
  }
}

async function toggleStaff(id, isActive) {
  try {
    await apiClient().patch(`/vendor/staff/${id}/active`, { is_active: isActive });
    toast(isActive ? 'تم تفعيل الموظف' : 'تم التعطيل — سُحبت صلاحية الدخول');
  } catch (e) {
    const msg = e.response?.data?.detail?.message || e.message;
    toast(msg, true);
    loadStaff();
  }
}

async function deleteStaff(id) {
  if (!confirm('حذف الموظف نهائياً؟')) return;
  try {
    await apiClient().delete(`/vendor/staff/${id}`);
    toast('تم الحذف');
    loadStaff();
  } catch (e) {
    toast(e.response?.data?.detail?.message || e.message, true);
  }
}

document.getElementById('staffForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await apiClient().post('/vendor/staff', {
      name: document.getElementById('staffName').value.trim(),
      phone: document.getElementById('staffPhone').value.trim(),
      password: document.getElementById('staffPassword').value,
      role: document.getElementById('staffRole').value,
    });
    toast('تم إضافة الموظف');
    e.target.reset();
    loadStaff();
  } catch (err) {
    toast(err.response?.data?.detail?.message || err.message, true);
  }
});

document.getElementById('refreshBtn').addEventListener('click', loadStaff);
document.getElementById('saveConfigBtn').addEventListener('click', saveConfig);

applyConfig();
loadStaff();
