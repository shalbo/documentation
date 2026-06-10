(function () {
  const form = document.getElementById("searchForm");
  const results = document.getElementById("results");

  function render(rows) {
    if (!rows.length) {
      results.innerHTML = '<p class="empty">لا نتائج</p>';
      return;
    }
    results.innerHTML = `
      <table class="data-table">
        <thead>
          <tr><th>رقم القطعة</th><th>الاسم</th><th>الفئة</th><th>السعر</th><th>ضمان</th></tr>
        </thead>
        <tbody>
          ${rows.map((p) => `
            <tr>
              <td><code>${p.part_number}</code></td>
              <td>${p.name || p.name_ar}${p.is_oem ? ' <span class="badge">OEM</span>' : ""}</td>
              <td>${p.category?.name || "—"}</td>
              <td>${p.price_sar} ر.س</td>
              <td>${p.warranty_months} شهر</td>
            </tr>`).join("")}
        </tbody>
      </table>`;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const q = document.getElementById("query").value.trim();
    const make = document.getElementById("make").value.trim();
    const model = document.getElementById("model").value.trim();
    const oem = document.getElementById("oemOnly").checked;
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (make) params.set("make", make);
    if (model) params.set("model", model);
    if (oem) params.set("oem_only", "true");
    try {
      const res = await RoustoApi.get(`/parts/search?${params}`);
      render(res.data || []);
    } catch (err) {
      results.innerHTML = `<p class="error">${err.message}</p>`;
    }
  });
})();
