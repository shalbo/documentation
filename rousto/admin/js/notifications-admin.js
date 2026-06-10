const STORAGE_KEY = "rousto_admin_config";
const state = { apiBase: "http://localhost:8000", adminKey: "rousto_admin_dev" };
const $ = (sel) => document.querySelector(sel);

function loadConfig() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    if (saved.apiBase) state.apiBase = saved.apiBase;
    if (saved.adminKey) state.adminKey = saved.adminKey;
  } catch (_) {}
  $("#apiBase").value = state.apiBase;
  $("#adminKey").value = state.adminKey;
}

function saveConfig() {
  state.apiBase = $("#apiBase").value.replace(/\/$/, "");
  state.adminKey = $("#adminKey").value.trim();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function toast(msg, isError) {
  const el = $("#toast");
  el.textContent = msg;
  el.className = "toast show" + (isError ? " error" : "");
  setTimeout(() => el.classList.remove("show"), 2800);
}

function createNotificationsService() {
  return new NotificationsService(
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

async function api(path, options = {}) {
  const client = RoustoApiClient.createAdminClient({
    getApiBase: () => {
      saveConfig();
      return state.apiBase;
    },
    getAdminKey: () => {
      saveConfig();
      return state.adminKey;
    },
  });
  if (options.method === "POST") {
    return client.post(path, JSON.parse(options.body || "{}"));
  }
  return client.get(path);
}

function fmtDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString("ar-SA", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (_) {
    return iso;
  }
}

function renderAnalytics(data) {
  const items = [
    ["إجمالي الصندوق", data.inbox_total],
    ["غير مقروء", data.inbox_unread],
    ["Push مُرسل", data.push_sent_total],
    ["إرسال 24س", data.dispatches_24h],
    ["إرسال 7أ", data.dispatches_7d],
    ["بثوث", data.broadcasts_total],
    ["قوالب نشطة", data.templates_active],
    ["تخطى تفضيلات", data.skipped_by_preferences],
  ];
  $("#analyticsGrid").innerHTML = items
    .map(([l, v]) => `<div><b>${v}</b><div style="color:#888;font-size:.85rem">${l}</div></div>`)
    .join("");
}

function renderDispatchLog(rows) {
  const tbody = $("#dispatchLogBody");
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">لا سجلات</td></tr>';
    return;
  }
  tbody.innerHTML = rows
    .map(
      (r) =>
        `<tr>
          <td><small>${fmtDate(r.created_at)}</small></td>
          <td>${r.event_source}</td>
          <td>${r.user_name || r.user_id}<br><small>${r.user_phone || ""}</small></td>
          <td>${r.category}</td>
          <td>${r.title}</td>
          <td><span class="log-status ${r.status}">${r.status}</span></td>
        </tr>`
    )
    .join("");
}

function renderTemplates(rows) {
  const tbody = $("#templatesBody");
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty">لا قوالب</td></tr>';
    return;
  }
  tbody.innerHTML = rows
    .map(
      (t) =>
        `<tr>
          <td><code>${t.slug}</code></td>
          <td>${t.category}</td>
          <td>${t.title_template}</td>
          <td>${t.is_active ? "✓" : "—"}</td>
        </tr>`
    )
    .join("");
}

function renderInbox(rows) {
  const tbody = $("#inboxBody");
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">لا إشعارات</td></tr>';
    return;
  }
  tbody.innerHTML = rows
    .map(
      (n) =>
        `<tr>
          <td>${n.user_id}</td>
          <td>${n.category}</td>
          <td>${n.title}</td>
          <td>${n.is_read ? "✓" : "—"}</td>
          <td>${n.push_sent ? "✓" : "—"}</td>
          <td><small>${fmtDate(n.created_at)}</small></td>
        </tr>`
    )
    .join("");
}

function renderBroadcasts(rows) {
  const tbody = $("#broadcastsBody");
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty">لا بثوث</td></tr>';
    return;
  }
  tbody.innerHTML = rows
    .map(
      (b) =>
        `<tr>
          <td>${b.reference}</td>
          <td>${b.target_segment}</td>
          <td>${b.recipients_count} (${b.in_app_count} inbox)</td>
          <td>${b.push_sent_count}</td>
          <td><small>${fmtDate(b.created_at)}</small></td>
        </tr>`
    )
    .join("");
}

async function refresh() {
  try {
    const [analytics, log, templates, inbox, broadcasts] = await Promise.all([
      api("/admin/notifications/analytics"),
      api("/admin/notifications/dispatch-log?limit=50"),
      api("/admin/notifications/templates"),
      api("/admin/notifications?limit=50"),
      api("/admin/notifications/broadcasts"),
    ]);
    renderAnalytics(analytics.data);
    renderDispatchLog(log.data);
    renderTemplates(templates.data);
    renderInbox(inbox.data);
    renderBroadcasts(broadcasts.data);
    toast("تم التحديث");
  } catch (e) {
    toast(e.message, true);
  }
}

async function searchUsers(q) {
  if (!q || q.length < 2) return;
  try {
    const res = await createNotificationsService().searchUsers(q);
    const sel = $("#userSelect");
    sel.innerHTML = res.data
      .map(
        (u) =>
          `<option value="${u.id}">${u.full_name} — ${u.phone}</option>`
      )
      .join("");
  } catch (e) {
    toast(e.message, true);
  }
}

document.querySelectorAll(".tabs button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tabs button").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("panel-" + btn.dataset.tab).classList.add("active");
  });
});

$("#connectBtn").addEventListener("click", refresh);

let searchTimer;
$("#userSearch").addEventListener("input", (e) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => searchUsers(e.target.value.trim()), 350);
});

$("#sendForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const userId = $("#userSelect").value;
  if (!userId) return toast("اختر مستخدماً", true);
  try {
    await createNotificationsService().sendTest({
      user_id: userId,
      category: $("#sendCategory").value,
      title: $("#sendTitle").value,
      body: $("#sendBody").value,
      send_push: $("#sendPush").checked,
    });
    toast("تم الإرسال");
    refresh();
  } catch (err) {
    toast(err.message, true);
  }
});

$("#broadcastForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const res = await createNotificationsService().broadcast({
      target_segment: $("#broadcastSegment").value,
      category: $("#broadcastCategory").value,
      title: $("#broadcastTitle").value,
      body: $("#broadcastBody").value,
      send_push: $("#broadcastPush").checked,
    });
    toast(`بث ${res.data.reference}: ${res.data.recipients_count} مستلم`);
    refresh();
  } catch (err) {
    toast(err.message, true);
  }
});

loadConfig();
refresh();
