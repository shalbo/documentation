const STORAGE_KEY = "rousto_admin_config";
const $ = (id) => document.getElementById(id);

function cfg() {
  const apiBase = $("apiBase").value.replace(/\/$/, "");
  const adminKey = $("adminKey").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase, adminKey }));
  return { apiBase, adminKey };
}

function createPartsService() {
  return new PartsService(
    RoustoApiClient.createAdminClient({
      getApiBase: () => $("apiBase").value.replace(/\/$/, ""),
      getAdminKey: () => $("adminKey").value.trim(),
      onConfigSave: ({ apiBase, adminKey }) => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase, adminKey }));
      },
    })
  );
}

function toast(msg) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast show";
  setTimeout(() => el.classList.remove("show"), 2400);
}

async function refresh() {
  const partsSvc = createPartsService();
  try {
    const [parts, claims] = await Promise.all([
      partsSvc.listParts(),
      partsSvc.listWarrantyClaims(),
    ]);
    const tbody = $("partsBody");
    tbody.innerHTML = parts.data.length
      ? parts.data.map((p) => `
        <tr>
          <td><code>${p.oem_number || p.part_number}</code></td>
          <td>${p.name_ar || p.name}</td>
          <td>${p.vin_prefix || "—"}</td>
          <td>${p.category?.name_ar || p.category?.slug || "—"}</td>
          <td>${p.is_oem ? "✓ OEM" : "—"}</td>
          <td>${p.price_sar} ر.س</td>
        </tr>`).join("")
      : '<tr><td colspan="6" class="empty">لا قطع</td></tr>';

    const cbody = $("claimsBody");
    cbody.innerHTML = claims.data.length
      ? claims.data.map((c) => `
        <tr>
          <td>${c.id}</td>
          <td>${c.status}</td>
          <td>${c.description?.slice(0, 60) || "—"}</td>
        </tr>`).join("")
      : '<tr><td colspan="3" class="empty">لا مطالبات</td></tr>';
  } catch (e) {
    toast(e.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    if (saved.apiBase) $("apiBase").value = saved.apiBase;
    if (saved.adminKey) $("adminKey").value = saved.adminKey;
  } catch (_) {}
  refresh();
  $("refreshBtn")?.addEventListener("click", refresh);
});
