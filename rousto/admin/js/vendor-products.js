const STORAGE_KEY = "rousto_vendor_products_config";
const $ = (id) => document.getElementById(id);

function cfg() {
  const apiBase = $("apiBase").value.replace(/\/$/, "");
  const vendorId = $("vendorId").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase, vendorId }));
  return { apiBase, vendorId };
}

function toast(msg, err) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast show" + (err ? " error" : "");
  setTimeout(() => el.classList.remove("show"), 2800);
}

async function vendorApi(path, opts = {}) {
  const { apiBase, vendorId } = cfg();
  const res = await fetch(`${apiBase}/api/v1${path}`, {
    ...opts,
    headers: {
      "Content-Type": "application/json",
      "X-Vendor-Id": vendorId,
      ...(opts.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.error?.message || `خطأ ${res.status}`);
  return body;
}

async function loadRoots() {
  const { data } = await vendorApi("/vendor/parts/categories/roots");
  const sel = $("rootCategory");
  sel.innerHTML = '<option value="">— اختر القسم الرئيسي —</option>';
  data.forEach((r) => {
    const o = document.createElement("option");
    o.value = r.id;
    o.textContent = r.name_ar || r.name;
    sel.appendChild(o);
  });
}

async function loadChildren(parentId) {
  const sub = $("subCategory");
  sub.innerHTML = '<option value="">— اختر القسم الفرعي —</option>';
  if (!parentId) {
    sub.disabled = true;
    return;
  }
  const { data } = await vendorApi(`/vendor/parts/categories/${parentId}/children`);
  sub.disabled = false;
  if (!data.length) {
    toast("لا توجد أقسام فرعية لهذا القسم", true);
    sub.disabled = true;
    return;
  }
  data.forEach((c) => {
    const o = document.createElement("option");
    o.value = c.id;
    o.textContent = c.name_ar || c.name;
    sub.appendChild(o);
  });
}

$("rootCategory").addEventListener("change", (e) => {
  loadChildren(e.target.value).catch((err) => toast(err.message, true));
});

$("productForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const categoryId = $("subCategory").value;
  if (!categoryId) {
    toast("يجب اختيار قسم فرعي قبل الحفظ", true);
    return;
  }
  try {
    const body = await vendorApi("/vendor/parts", {
      method: "POST",
      body: JSON.stringify({
        category_id: categoryId,
        part_number: $("partNumber").value.trim(),
        slug: $("slug").value.trim(),
        name_ar: $("nameAr").value.trim(),
        price_sar: parseFloat($("price").value),
        qty_available: parseInt($("qty").value, 10),
        oem_number: $("oemNumber").value.trim() || null,
        vin_prefix: $("vinPrefix").value.trim() || null,
        is_oem: $("isOem").checked,
      }),
    });
    toast(`تم حفظ المنتج: ${body.data.name_ar || body.data.name}`);
    $("productForm").reset();
    $("subCategory").disabled = true;
  } catch (err) {
    toast(err.message, true);
  }
});

try {
  const s = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  if (s.apiBase) $("apiBase").value = s.apiBase;
  if (s.vendorId) $("vendorId").value = s.vendorId;
} catch (_) {}

loadRoots().catch((e) => toast(e.message, true));
