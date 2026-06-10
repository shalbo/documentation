const cities = ['طرابلس', 'مصراتة', 'بنغازي', 'الزاوية', 'سبها', 'البيضاء'];
const citySel = document.getElementById('city');
cities.forEach((c) => {
  const o = document.createElement('option');
  o.value = c;
  o.textContent = c;
  citySel.appendChild(o);
});

let role = 'vendor';
document.getElementById('tabVendor').onclick = () => setRole('vendor');
document.getElementById('tabWorkshop').onclick = () => setRole('workshop');

function setRole(r) {
  role = r;
  document.getElementById('role').value = r;
  document.getElementById('tabVendor').classList.toggle('active', r === 'vendor');
  document.getElementById('tabWorkshop').classList.toggle('active', r === 'workshop');
  document.getElementById('bizLabel').textContent = r === 'vendor' ? 'اسم المحل' : 'اسم المركز';
}

document.getElementById('mapPick').onclick = () => {
  const picks = [
    { lat: 32.8872, lng: 13.1913, label: 'طرابلس' },
    { lat: 32.3754, lng: 15.0925, label: 'مصراتة' },
    { lat: 32.1167, lng: 20.0667, label: 'بنغازي' },
  ];
  const p = picks[Math.floor(Math.random() * picks.length)];
  document.getElementById('lat').value = p.lat;
  document.getElementById('lng').value = p.lng;
  document.getElementById('mapPick').textContent = `تم: ${p.label} (${p.lat}, ${p.lng})`;
};

function toast(msg, err) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show' + (err ? ' error' : '');
  setTimeout(() => el.classList.remove('show'), 2500);
}

document.getElementById('regForm').onsubmit = async (e) => {
  e.preventDefault();
  const base = 'http://localhost:8000';
  const path = role === 'vendor' ? '/api/v1/registration/vendor' : '/api/v1/registration/workshop';
  const payload = {
    full_name: document.getElementById('fullName').value,
    phone: document.getElementById('phone').value,
    email: document.getElementById('email').value,
    specialty: document.getElementById('specialty').value || null,
    city: document.getElementById('city').value,
    latitude: parseFloat(document.getElementById('lat').value),
    longitude: parseFloat(document.getElementById('lng').value),
  };
  if (role === 'vendor') payload.shop_name = document.getElementById('bizName').value;
  else payload.center_name = document.getElementById('bizName').value;

  try {
    const res = await fetch(base + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const body = await res.json();
    if (!res.ok) throw new Error(body.detail?.message || 'فشل التسجيل');
    toast('تم إرسال الطلب — بانتظار اعتماد الإدارة');
    e.target.reset();
  } catch (err) {
    toast(err.message, true);
  }
};
