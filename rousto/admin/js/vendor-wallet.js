const KEY = "rousto_vendor_config";
const state = { apiBase: "http://localhost:8000", vendorId: "" };
const $ = (s) => document.querySelector(s);

function cfg() {
  try {
    const s = JSON.parse(localStorage.getItem(KEY) || "{}");
    if (s.apiBase) state.apiBase = s.apiBase;
    if (s.vendorId) state.vendorId = s.vendorId;
  } catch (_) {}
  $("#apiBase").value = state.apiBase;
  $("#vendorId").value = state.vendorId || "v0000000-0000-4000-8000-000000000001";
}

function createWalletService() {
  return new VendorWalletService(
    RoustoApiClient.createVendorClient({
      getApiBase: () => $("#apiBase").value.replace(/\/$/, ""),
      getVendorId: () => $("#vendorId").value.trim(),
      onConfigSave: ({ apiBase, vendorId }) => {
        state.apiBase = apiBase;
        state.vendorId = vendorId;
        localStorage.setItem(KEY, JSON.stringify(state));
      },
    })
  );
}

function toast(m, err) {
  const el = $("#toast");
  el.textContent = m;
  el.className = "toast show" + (err ? " error" : "");
  setTimeout(() => el.classList.remove("show"), 2800);
}

function render(data) {
  $("#balanceLyd").textContent = `${Number(data.balance_lyd).toFixed(2)} د.ل`;
  $("#pendingLyd").textContent = `${Number(data.pending_withdrawals_lyd || data.pending_lyd || 0).toFixed(2)} د.ل`;
  const txs = data.transactions || [];
  $("#txList").innerHTML = txs.length
    ? txs.map((t) => {
        const cls = t.direction === "credit" ? "tx-credit" : "tx-debit";
        const sign = t.direction === "credit" ? "+" : "−";
        return `<div class="tx-item"><span>${t.description_ar || t.transaction_type}</span><span class="${cls}">${sign}${t.amount_lyd} د.ل</span></div>`;
      }).join("")
    : '<div class="empty">لا توجد عمليات</div>';
}

async function load() {
  const wallet = createWalletService();
  try {
    const body = await wallet.getWallet();
    render(body.data);
  } catch (e) {
    toast(e.message, true);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  cfg();
  load();
  $("#refreshBtn").onclick = load;
  $("#withdrawForm").onsubmit = async (e) => {
    e.preventDefault();
    const wallet = createWalletService();
    try {
      const body = await wallet.requestWithdrawal({
        amountLyd: Number($("#amount").value),
        iban: $("#iban").value || null,
        note: $("#note").value || null,
      });
      toast(body.message || body.meta?.message || "تم إرسال الطلب");
      load();
    } catch (err) {
      toast(err.message, true);
    }
  };
});
