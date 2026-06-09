const STORAGE_KEY = "rousto_support_config";
const state = { apiBase: "http://localhost:8000", userId: "", selectedTicketId: null };

const $ = (id) => document.getElementById(id);

function loadConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    if (saved.apiBase) state.apiBase = saved.apiBase;
    if (saved.userId) state.userId = saved.userId;
  } catch (_) {}
  $("apiBase").value = state.apiBase;
  $("userId").value = state.userId || "a0000000-0000-4000-8000-000000000001";
}

function saveConfig() {
  state.apiBase = $("apiBase").value.replace(/\/$/, "");
  state.userId = $("userId").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ apiBase: state.apiBase, userId: state.userId }));
}

function toast(msg) {
  const el = $("toast");
  el.textContent = msg;
  el.className = "toast show";
  setTimeout(() => el.classList.remove("show"), 2400);
}

async function api(path, options = {}) {
  saveConfig();
  const res = await fetch(`${state.apiBase}/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-User-Id": state.userId,
      ...(options.headers || {}),
    },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.error?.message || `خطأ ${res.status}`);
  return body;
}

function renderFaq(items) {
  $("faqList").innerHTML = items.length
    ? items.map((f) => `<div class="faq-item"><h3>${f.question_ar}</h3><p>${f.answer_ar}</p></div>`).join("")
    : "<p>لا توجد أسئلة</p>";
}

function renderTickets(tickets) {
  $("ticketList").innerHTML = tickets.length
    ? tickets.map((t) => `
      <div class="ticket-card" data-id="${t.id}">
        <b>${t.reference}</b> · ${t.status_label_ar}<br>
        <small>${t.subject}</small>
      </div>`).join("")
    : "<p>لا توجد تذاكر</p>";
}

function renderTicketDetail(ticket) {
  state.selectedTicketId = ticket.id;
  $("ticketDetail").style.display = "block";
  $("detailSubject").textContent = `${ticket.reference} — ${ticket.subject}`;
  $("messages").innerHTML = (ticket.messages || [])
    .map((m) => `<div class="msg ${m.author_type}"><b>${m.author_label}</b><br>${m.message}</div>`)
    .join("");
}

async function loadAll() {
  const [faq, tickets, security] = await Promise.all([
    api("/support/faq"),
    api("/support/tickets"),
    api("/me/security"),
  ]);
  renderFaq(faq.data || []);
  renderTickets(tickets.data || []);
  $("securitySummary").textContent =
    `تذاكر مفتوحة: ${security.data.open_tickets_count} · تنبيهات الدخول: ${security.data.login_alerts_enabled ? "مفعّلة" : "معطّلة"}`;
}

$("refreshBtn").addEventListener("click", () => loadAll().then(() => toast("تم التحديث")).catch((e) => toast(e.message)));

$("ticketForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const body = await api("/support/tickets", {
      method: "POST",
      body: JSON.stringify({
        category: $("category").value,
        priority: $("priority").value,
        subject: $("subject").value.trim(),
        message: $("message").value.trim(),
      }),
    });
    toast(`تم إنشاء ${body.data.reference}`);
    e.target.reset();
    await loadAll();
    renderTicketDetail(body.data);
  } catch (err) {
    toast(err.message);
  }
});

$("ticketList").addEventListener("click", async (e) => {
  const card = e.target.closest("[data-id]");
  if (!card) return;
  try {
    const body = await api(`/support/tickets/${card.dataset.id}`);
    renderTicketDetail(body.data);
  } catch (err) {
    toast(err.message);
  }
});

$("replyForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!state.selectedTicketId) return;
  try {
    const body = await api(`/support/tickets/${state.selectedTicketId}/messages`, {
      method: "POST",
      body: JSON.stringify({ message: $("replyMessage").value.trim() }),
    });
    renderTicketDetail(body.data);
    $("replyMessage").value = "";
    toast("تم إرسال الرد");
  } catch (err) {
    toast(err.message);
  }
});

$("reportForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/me/security/report", {
      method: "POST",
      body: JSON.stringify({ description: $("reportDesc").value.trim() }),
    });
    $("reportDesc").value = "";
    toast("تم تسجيل البلاغ");
    await loadAll();
  } catch (err) {
    toast(err.message);
  }
});

loadConfig();
loadAll().catch(() => {});
