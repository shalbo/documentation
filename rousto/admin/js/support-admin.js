const STORAGE_KEY = "rousto_admin_config";
const state = { apiBase: "http://localhost:8000", adminKey: "rousto_admin_dev", tickets: [], selectedId: null };

const $ = (id) => document.getElementById(id);

function loadConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    if (saved.apiBase) state.apiBase = saved.apiBase;
    if (saved.adminKey) state.adminKey = saved.adminKey;
  } catch (_) {}
  $("apiBase").value = state.apiBase;
  $("adminKey").value = state.adminKey;
}

function saveConfig() {
  state.apiBase = $("apiBase").value.replace(/\/$/, "");
  state.adminKey = $("adminKey").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase: state.apiBase, adminKey: state.adminKey }));
}

function toast(msg, err = false) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast show" + (err ? " error" : "");
  setTimeout(() => el.classList.remove("show"), 2800);
}

function createSupportService() {
  return new SupportService(
    RoustoApiClient.createAdminClient({
      getApiBase: () => {
        saveConfig();
        return state.apiBase;
      },
      getAdminKey: () => {
        saveConfig();
        return state.adminKey;
      },
    })
  );
}

function renderTable() {
  const tbody = $("ticketsTable").querySelector("tbody");
  if (!state.tickets.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty">لا توجد تذاكر</td></tr>';
    return;
  }
  tbody.innerHTML = state.tickets.map((t) => `
    <tr>
      <td><b>${t.reference}</b></td>
      <td>${t.subject}</td>
      <td><span class="badge badge-warn">${t.status_label_ar}</span></td>
      <td><button class="btn btn-ghost" data-open="${t.id}">عرض</button></td>
    </tr>`).join("");
}

function renderDetail(ticket) {
  $("detailTitle").textContent = `${ticket.reference} — ${ticket.subject}`;
  $("messages").innerHTML = (ticket.messages || [])
    .map((m) => `<div class="msg ${m.author_type}"><b>${m.author_label}</b> · <small>${new Date(m.created_at).toLocaleString("ar-SA")}</small><br>${m.message}</div>`)
    .join("");
}

async function openTicket(id) {
  const body = await createSupportService().getTicket(id);
  state.selectedId = id;
  renderDetail(body.data);
}

async function refresh() {
  const body = await createSupportService().listTickets();
  state.tickets = body.data || [];
  renderTable();
  if (state.selectedId) await openTicket(state.selectedId);
  toast(`تم تحميل ${state.tickets.length} تذكرة`);
}

$("refreshBtn").addEventListener("click", () => refresh().catch((e) => toast(e.message, true)));
$("ticketsTable").addEventListener("click", (e) => {
  const id = e.target.closest("[data-open]")?.dataset.open;
  if (id) openTicket(id).catch((err) => toast(err.message, true));
});

$("replyForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!state.selectedId) return;
  try {
    await createSupportService().reply(state.selectedId, {
      message: $("replyText").value.trim(),
      status: $("replyStatus").value,
    });
    $("replyText").value = "";
    await refresh();
    toast("تم إرسال الرد");
  } catch (err) {
    toast(err.message, true);
  }
});

loadConfig();
refresh().catch(() => {});
