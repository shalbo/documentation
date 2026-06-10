const STORAGE_KEY = "rousto_vendor_products_config";
const $ = (id) => document.getElementById(id);

let bulkFile = null;
let zipFile = null;

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

function setProgress(prefix, pct, label) {
  const wrap = $(`${prefix}Progress`);
  const fill = $(`${prefix}ProgressFill`);
  const lbl = $(`${prefix}ProgressLabel`);
  wrap.classList.add("show");
  fill.style.width = `${pct}%`;
  lbl.textContent = label || `${pct}%`;
  if (pct >= 100) {
    setTimeout(() => wrap.classList.remove("show"), 1200);
  }
}

function uploadWithProgress(url, formData, vendorId, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.setRequestHeader("X-Vendor-Id", vendorId);
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        const pct = Math.round((e.loaded / e.total) * 90);
        onProgress(pct, `جاري الرفع… ${pct}%`);
      }
    };
    xhr.onload = () => {
      let body = {};
      try {
        body = JSON.parse(xhr.responseText || "{}");
      } catch (_) {}
      resolve({ status: xhr.status, body });
    };
    xhr.onerror = () => reject(new Error("فشل الاتصال بالخادم"));
    xhr.send(formData);
  });
}

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
  $("bulkUploadBtn").disabled = true;
  setProgress("bulk", 0, "بدء الرفع…");
  try {
    const { status, body } = await uploadWithProgress(
      `${apiBase}/api/v1/vendor/parts/bulk-upload`,
      form,
      vendorId,
      (pct, lbl) => setProgress("bulk", pct, lbl)
    );
    setProgress("bulk", 95, "جاري المعالجة…");
    if (status < 200 || status >= 300) {
      const data = body?.error?.data || {
        imported: 0,
        failed: body?.error?.data?.failed,
        errors: body?.error?.data?.errors,
        total_rows: body?.error?.data?.total_rows,
      };
      showBulkResult(data, true);
      toast(body?.error?.message || "فشل الرفع", true);
      return;
    }
    setProgress("bulk", 100, "اكتمل");
    showBulkResult(body.data, false);
    toast(body.meta?.message || "تم الرفع بنجاح");
    bulkFile = null;
    $("bulkFileName").textContent = "";
    fileInput.value = "";
  } catch (err) {
    toast(err.message, true);
  } finally {
    $("bulkUploadBtn").disabled = !bulkFile;
  }
});

function setZipFile(file) {
  zipFile = file;
  if (!file.name.toLowerCase().endsWith(".zip")) {
    toast("الصيغة المدعومة: .zip فقط", true);
    zipFile = null;
    $("zipFileName").textContent = "";
    $("zipUploadBtn").disabled = true;
    return;
  }
  $("zipFileName").textContent = file.name;
  $("zipUploadBtn").disabled = false;
}

const zipDropZone = $("zipDropZone");
const zipInput = $("zipFileInput");

zipDropZone.addEventListener("click", () => zipInput.click());
zipInput.addEventListener("change", (e) => {
  if (e.target.files[0]) setZipFile(e.target.files[0]);
});
zipDropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  zipDropZone.classList.add("dragover");
});
zipDropZone.addEventListener("dragleave", () => zipDropZone.classList.remove("dragover"));
zipDropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  zipDropZone.classList.remove("dragover");
  if (e.dataTransfer.files[0]) setZipFile(e.dataTransfer.files[0]);
});

function showZipResult(payload, isError) {
  const panel = $("zipResult");
  const stats = $("zipStats");
  const errors = $("zipErrors");
  panel.className = "result-panel show " + (isError ? "error" : "success");
  stats.innerHTML = `
    <span class="stat-pill ok">مربوطة: ${payload.linked || 0}</span>
    <span class="stat-pill fail">أخطاء: ${payload.failed || 0}</span>
    <span class="stat-pill warn">ملفات: ${payload.total_files || 0}</span>
    ${payload.unmatched?.length ? `<span class="stat-pill warn">بدون تطابق: ${payload.unmatched.length}</span>` : ""}
  `;
  errors.innerHTML = "";
  (payload.errors || []).forEach((e) => {
    const li = document.createElement("li");
    li.textContent = `${e.file}: ${e.message}`;
    errors.appendChild(li);
  });
  (payload.unmatched || []).forEach((f) => {
    const li = document.createElement("li");
    li.textContent = `بدون قطعة مطابقة: ${f}`;
    li.style.color = "var(--brand-navy)";
    errors.appendChild(li);
  });
}

$("zipUploadBtn").addEventListener("click", async () => {
  if (!zipFile) return;
  const { apiBase, vendorId } = cfg();
  const form = new FormData();
  form.append("file", zipFile);
  $("zipUploadBtn").disabled = true;
  setProgress("zip", 0, "بدء رفع الأرشيف…");
  try {
    const { status, body } = await uploadWithProgress(
      `${apiBase}/api/v1/vendor/parts/bulk-images-zip`,
      form,
      vendorId,
      (pct, lbl) => setProgress("zip", pct, lbl)
    );
    setProgress("zip", 95, "جاري فك الضغط وربط الصور…");
    if (status < 200 || status >= 300) {
      showZipResult(body?.error?.data || { linked: 0, failed: 1, errors: [{ file: zipFile.name, message: body?.error?.message }] }, true);
      toast(body?.error?.message || "فشل ربط الصور", true);
      return;
    }
    setProgress("zip", 100, "اكتمل");
    showZipResult(body.data, false);
    toast(body.meta?.message || "تم ربط الصور");
    zipFile = null;
    $("zipFileName").textContent = "";
    zipInput.value = "";
  } catch (err) {
    toast(err.message, true);
  } finally {
    $("zipUploadBtn").disabled = !zipFile;
  }
});

function syncConditionUi() {
  const isUsed = $("condUsed").checked;
  $("condNewLbl").classList.toggle("active", !isUsed);
  $("condUsedLbl").classList.toggle("used-active", isUsed);
  $("condUsedLbl").classList.toggle("active", false);
}

document.querySelectorAll('input[name="partCondition"]').forEach((el) => {
  el.addEventListener("change", syncConditionUi);
});
syncConditionUi();

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
        part_condition: document.querySelector('input[name="partCondition"]:checked')?.value || "new",
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

if (window.VendorStoreStatus) {
  VendorStoreStatus.bind(vendorApi, toast);
}
