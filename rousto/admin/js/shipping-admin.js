const STORAGE_KEY = "rousto_admin_config";
const $ = (id) => document.getElementById(id);

function cfg() {
  const apiBase = $("apiBase").value.replace(/\/$/, "");
  const adminKey = $("adminKey").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase, adminKey }));
  return { apiBase, adminKey };
}

function toast(msg) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast show";
  setTimeout(() => el.classList.remove("show"), 2400);
}

async function adminApi(path, opts = {}) {
  const { apiBase, adminKey } = cfg();
  const res = await fetch(`${apiBase}/api/v1${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Key": adminKey,
      ...(opts.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.error?.message || `خطأ ${res.status}`);
  return body;
}

async function refresh() {
  try {
    const { data } = await adminApi("/admin/shipping/intercity-rates");
    $("ratesBody").innerHTML = data.length
      ? data.map((r) => `<tr>
          <td>${r.origin_city}</td><td>${r.destination_city}</td>
          <td>${r.flat_fee_sar} ر.س</td><td>${r.carrier_name}</td>
          <td>${r.eta_days} يوم</td><td>${r.is_active ? "نشط" : "معطّل"}</td>
        </tr>`).join("")
      : '<tr><td colspan="6" class="empty">لا تعرفات</td></tr>';
    toast(`تم تحميل ${data.length} تعرفة`);
  } catch (e) {
    toast(e.message);
  }
}

$("refreshBtn").addEventListener("click", refresh);

$("rateForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await adminApi("/admin/shipping/intercity-rates", {
      method: "POST",
      body: JSON.stringify({
        origin_city: $("originCity").value.trim(),
        destination_city: $("destCity").value.trim(),
        flat_fee_sar: parseFloat($("flatFee").value),
        carrier_name: $("carrierName").value.trim(),
        carrier_slug: $("carrierSlug").value.trim(),
        eta_days: parseInt($("etaDays").value, 10),
      }),
    });
    toast("تمت إضافة التعرفة");
    refresh();
  } catch (err) {
    toast(err.message);
  }
});

$("quoteBtn").addEventListener("click", async () => {
  const { apiBase } = cfg();
  try {
    const res = await fetch(`${apiBase}/api/v1/shipping/quote`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        origin_city: $("quoteOrigin").value.trim(),
        destination_city: $("quoteDest").value.trim(),
      }),
    });
    const body = await res.json();
    $("quoteOut").textContent = JSON.stringify(body.data, null, 2);
  } catch (e) {
    toast(e.message);
  }
});

try {
  const s = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  if (s.apiBase) $("apiBase").value = s.apiBase;
  if (s.adminKey) $("adminKey").value = s.adminKey;
} catch (_) {}
refresh();
