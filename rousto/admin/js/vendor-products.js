const STORAGE_KEY = "rousto_vendor_products_config";
const $ = (id) => document.getElementById(id);

let bulkFile = null;

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
      "X-Vendor-Id": vendorId,
      ...(opts.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(body?.error?.message || `خطأ ${res.status}`);
    err.status = res.status;
    err.payload = body?.error?.data || body?.error || body;
    throw err;
  }
  return body;
}

function parseVinPrefixes(raw) {
  if (!raw || !raw.trim()) return [];
  return raw
    .split(/[\s,;]+/)
    .map((s) => s.trim().toUpperCase())
    .filter((s) => s.length >= 11)
    .map((s) => s.slice(0, 11));
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

function setTab(name) {
  document.querySelectorAll(".tab-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.tab === name);
  });
  document.querySelectorAll(".tab-panel").forEach((p) => {
    p.classList.toggle("active", p.id === `panel-${name}`);
  });
}

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => setTab(btn.dataset.tab));
});

function setBulkFile(file) {
  bulkFile = file;
  const ext = file.name.split(".").pop().toLowerCase();
  if (!["csv", "xlsx"].includes(ext)) {
    toast("الصيغ المدعومة: .csv و .xlsx فقط", true);
    bulkFile = null;
    $("bulkFileName").textContent = "";
    $("bulkUploadBtn").disabled = true;
    return;
  }
  $("bulkFileName").textContent = file.name;
  $("bulkUploadBtn").disabled = false;
}

const dropZone = $("dropZone");
const fileInput = $("bulkFileInput");

dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (e) => {
  if (e.target.files[0]) setBulkFile(e.target.files[0]);
});

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  if (e.dataTransfer.files[0]) setBulkFile(e.dataTransfer.files[0]);
});

function showBulkResult(payload, isError) {
  const panel = $("bulkResult");
  const stats = $("bulkStats");
  const errors = $("bulkErrors");
  panel.className = "result-panel show " + (isError ? "error" : "success");
  stats.innerHTML = `
    <span class="stat-pill ok">ناجح: ${payload.imported || 0}</span>
    <span class="stat-pill fail">أخطاء: ${payload.failed || 0}</span>
    <span class="stat-pill warn">إجمالي الصفوف: ${payload.total_rows || 0}</span>
    ${payload.used_uncategorized ? `<span class="stat-pill warn">غير مصنف: ${payload.used_uncategorized}</span>` : ""}
  `;
  errors.innerHTML = "";
  (payload.errors || []).forEach((e) => {
    const li = document.createElement("li");
    li.textContent = `صف ${e.row} — ${e.field}: ${e.message}`;
    errors.appendChild(li);
  });
}

$("templateLink").addEventListener("click", async (e) => {
  e.preventDefault();
  const { apiBase, vendorId } = cfg();
  try {
    const res = await fetch(`${apiBase}/api/v1/vendor/parts/bulk-upload/template`, {
      headers: { "X-Vendor-Id": vendorId },
    });
    if (!res.ok) throw new Error("تعذّر تحميل النموذج");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "rousto-parts-template.csv";
    a.click();
    URL.revokeObjectURL(url);
    toast("تم تحميل النموذج");
  } catch (err) {
    toast(err.message, true);
  }
});

$("bulkUploadBtn").addEventListener("click", async () => {
  if (!bulkFile) return;
  const { apiBase, vendorId } = cfg();
  const form = new FormData();
  form.append("file", bulkFile);
  $("bulkStatus").textContent = "جاري المعالجة…";
  $("bulkUploadBtn").disabled = true;
  try {
    const res = await fetch(`${apiBase}/api/v1/vendor/parts/bulk-upload`, {
      method: "POST",
      headers: { "X-Vendor-Id": vendorId },
      body: form,
    });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      const data = body?.error?.data || { failed: body?.error?.data?.failed, errors: body?.error?.data?.errors, total_rows: body?.error?.data?.total_rows, imported: 0 };
      showBulkResult(data, true);
      toast(body?.error?.message || "فشل الرفع", true);
      return;
    }
    showBulkResult(body.data, false);
    toast(body.meta?.message || "تم الرفع بنجاح");
    bulkFile = null;
    $("bulkFileName").textContent = "";
    fileInput.value = "";
  } catch (err) {
    toast(err.message, true);
  } finally {
    $("bulkStatus").textContent = "";
    $("bulkUploadBtn").disabled = !bulkFile;
  }
});

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
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        category_id: categoryId,
        part_number: $("partNumber").value.trim(),
        slug: $("slug").value.trim(),
        name_ar: $("nameAr").value.trim(),
        price_sar: parseFloat($("price").value),
        qty_available: parseInt($("qty").value, 10),
        oem_number: $("oemNumber").value.trim() || null,
        vin_prefixes: parseVinPrefixes($("vinPrefixes").value),
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
