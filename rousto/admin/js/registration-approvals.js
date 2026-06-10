const apiBase = () => document.getElementById('apiBase').value.replace(/\/$/, '');
const adminKey = () => document.getElementById('adminKey').value;

function toast(msg, isError = false) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show' + (isError ? ' error' : '');
  setTimeout(() => el.classList.remove('show'), 2800);
}

async function loadPending() {
  const list = document.getElementById('pendingList');
  list.innerHTML = 'جاري التحميل…';
  try {
    const res = await fetch(`${apiBase()}/api/v1/admin/registration/pending`, {
      headers: { 'X-Admin-Key': adminKey() },
    });
    const body = await res.json();
    if (!res.ok) throw new Error(body.detail?.message || 'فشل التحميل');
    const items = body.data || [];
    document.getElementById('countBadge').textContent = items.length;
    if (!items.length) {
      list.innerHTML = '<p class="empty">لا توجد طلبات معلّقة</p>';
      return;
    }
    list.innerHTML = items.map(renderCard).join('');
    list.querySelectorAll('[data-approve]').forEach((btn) => {
      btn.addEventListener('click', () => act(btn.dataset.approve, btn.dataset.id, 'approve'));
    });
    list.querySelectorAll('[data-reject]').forEach((btn) => {
      btn.addEventListener('click', () => {
        const reason = prompt('سبب الرفض:');
        if (reason) act(btn.dataset.reject, btn.dataset.id, 'reject', reason);
      });
    });
  } catch (e) {
    list.innerHTML = `<p class="empty">${e.message}</p>`;
  }
}

function renderCard(item) {
  const u = item.user || {};
  const roleLabel = { vendor: 'تاجر', driver: 'سائق', workshop: 'ورشة' }[item.role] || item.role;
  const title = item.shop_name || item.center_name || `${roleLabel} — ${u.full_name}`;
  const docs = item.role === 'driver'
    ? `<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
        ${docImg('رخصة', item.license_doc_path)}
        ${docImg('هوية', item.id_doc_path)}
        ${docImg('سيارة', item.vehicle_doc_path)}
      </div>`
    : '';
  return `<article class="card pending-card" style="margin-bottom:12px">
    <strong>${title}</strong>
    <div class="subheading">${roleLabel} · ${u.phone} · ${item.city || u.city || ''}</div>
    ${item.plate_number ? `<div>اللوحة: ${item.plate_number} · ${item.service_type}</div>` : ''}
    ${item.specialty ? `<div>التخصص: ${item.specialty}</div>` : ''}
    ${docs}
    <div class="actions-row">
      <button class="btn btn-approve" data-approve="${item.role}" data-id="${item.id}">اعتماد الحساب</button>
      <button class="btn btn-reject" data-reject="${item.role}" data-id="${item.id}">رفض الطلب</button>
    </div>
  </article>`;
}

function docImg(label, path) {
  if (!path) return `<span class="badge badge-off">${label}: غير مرفوع</span>`;
  const url = `${apiBase()}/files/${path}`;
  return `<figure><img class="doc-thumb" src="${url}" alt="${label}" onerror="this.style.display='none'" /><figcaption style="font-size:.7rem">${label}</figcaption></figure>`;
}

async function act(role, id, action, reason = '') {
  const path = action === 'approve' ? 'approve' : 'reject';
  const opts = {
    method: 'POST',
    headers: { 'X-Admin-Key': adminKey(), 'Content-Type': 'application/json' },
  };
  if (action === 'reject') opts.body = JSON.stringify({ reason });
  try {
    const res = await fetch(`${apiBase()}/api/v1/admin/registration/${role}/${id}/${path}`, opts);
    const body = await res.json();
    if (!res.ok) throw new Error(body.detail?.message || 'فشلت العملية');
    toast(action === 'approve' ? 'تم الاعتماد' : 'تم الرفض');
    loadPending();
  } catch (e) {
    toast(e.message, true);
  }
}

document.getElementById('refreshBtn').addEventListener('click', loadPending);
loadPending();
