/** Demo data loader for printable invoice template. */
(function () {
  const params = new URLSearchParams(window.location.search);
  const demo = {
    ref: params.get("ref") || "INV-2026-0042",
    date: params.get("date") || new Date().toLocaleDateString("ar-LY"),
    vendorName: params.get("vendor") || "محل الفلاتر الليبي",
    vendorCity: params.get("city") || "طرابلس",
    customerName: params.get("customer") || "أحمد محمد",
    customerPhone: params.get("phone") || "+218912345678",
    lines: [
      { desc: "فلتر زيت — OEM", qty: 2, price: 45 },
      { desc: "فلتر هواء", qty: 1, price: 32 },
    ],
    commission: 11.7,
  };

  const total = demo.lines.reduce((s, l) => s + l.qty * l.price, 0);
  const net = total - demo.commission;

  const set = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  set("invRef", demo.ref);
  set("invDate", demo.date);
  set("vendorName", demo.vendorName);
  set("vendorCity", demo.vendorCity);
  set("customerName", demo.customerName);
  set("customerPhone", demo.customerPhone);
  set("invTotal", total.toFixed(2));
  set("invCommission", demo.commission.toFixed(2));
  set("invNet", net.toFixed(2));

  const tbody = document.getElementById("invLines");
  if (tbody) {
    tbody.innerHTML = demo.lines.map((l) => `
      <tr>
        <td>${l.desc}</td>
        <td>${l.qty}</td>
        <td>${l.price.toFixed(2)}</td>
        <td>${(l.qty * l.price).toFixed(2)}</td>
      </tr>`).join("");
  }
})();
