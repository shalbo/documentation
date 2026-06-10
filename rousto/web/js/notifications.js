(function () {
  "use strict";

  var prefs = [];

  function fmtDate(iso) {
    if (!iso) return "";
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

  function renderList(items) {
    var el = document.getElementById("notifList");
    if (!el) return;
    if (!items.length) {
      el.innerHTML = '<p class="portal-empty">لا توجد إشعارات</p>';
      return;
    }
    el.innerHTML = items
      .map(function (n) {
        var cls = n.is_read ? "notif-item" : "notif-item unread";
        return (
          '<article class="' +
          cls +
          '" data-id="' +
          n.id +
          '">' +
          "<h3>" +
          escapeHtml(n.title) +
          "</h3>" +
          "<p>" +
          escapeHtml(n.body) +
          "</p>" +
          '<div class="notif-meta">' +
          '<span class="notif-cat">' +
          escapeHtml(n.category_label_ar || n.category) +
          "</span>" +
          "<span>" +
          fmtDate(n.created_at) +
          "</span>" +
          "</div></article>"
        );
      })
      .join("");

    el.querySelectorAll(".notif-item").forEach(function (item) {
      item.addEventListener("click", function () {
        var id = item.getAttribute("data-id");
        markRead(id).then(function () {
          loadNotifications();
        });
      });
    });
  }

  function escapeHtml(s) {
    return String(s || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function renderPrefs() {
    var el = document.getElementById("prefList");
    if (!el) return;
    el.innerHTML = prefs
      .map(function (p, i) {
        return (
          '<div class="pref-row">' +
          "<label>" +
          escapeHtml(p.category_label_ar || p.category) +
          "</label>" +
          '<div class="pref-toggles">' +
          '<label><input type="checkbox" data-idx="' +
          i +
          '" data-field="in_app_enabled" ' +
          (p.in_app_enabled ? "checked" : "") +
          " /> داخل التطبيق</label>" +
          '<label><input type="checkbox" data-idx="' +
          i +
          '" data-field="push_enabled" ' +
          (p.push_enabled ? "checked" : "") +
          " /> Push</label>" +
          "</div></div>"
        );
      })
      .join("");
  }

  function loadUnreadCount() {
    return RoustoAPI.getNotificationUnreadCount().then(function (res) {
      var count = (res.data && res.data.count) || 0;
      var badge = document.getElementById("unreadBadge");
      if (badge) badge.textContent = count + " غير مقروء";
    });
  }

  function loadNotifications() {
    var unreadOnly = document.getElementById("unreadOnly");
    var only = unreadOnly && unreadOnly.checked;
    return RoustoAPI.getNotifications({ unread_only: only })
      .then(function (res) {
        renderList(res.data || []);
        return loadUnreadCount();
      })
      .catch(function (err) {
        var el = document.getElementById("notifList");
        if (el) el.innerHTML = '<p class="portal-empty">' + escapeHtml(err.message) + "</p>";
      });
  }

  function loadPreferences() {
    return RoustoAPI.getNotificationPreferences()
      .then(function (res) {
        prefs = res.data || [];
        renderPrefs();
      })
      .catch(function (err) {
        RoustoToast(err.message, "error");
      });
  }

  function markRead(id) {
    return RoustoAPI.markNotificationRead(id).catch(function (err) {
      RoustoToast(err.message, "error");
    });
  }

  function init() {
    var refreshBtn = document.getElementById("refreshBtn");
    var readAllBtn = document.getElementById("readAllBtn");
    var unreadOnly = document.getElementById("unreadOnly");
    var savePrefsBtn = document.getElementById("savePrefsBtn");

    if (refreshBtn) {
      refreshBtn.addEventListener("click", function () {
        loadNotifications();
        loadPreferences();
      });
    }
    if (readAllBtn) {
      readAllBtn.addEventListener("click", function () {
        RoustoAPI.markAllNotificationsRead()
          .then(function () {
            RoustoToast("تم تعليم الكل كمقروء");
            loadNotifications();
          })
          .catch(function (err) {
            RoustoToast(err.message, "error");
          });
      });
    }
    if (unreadOnly) {
      unreadOnly.addEventListener("change", loadNotifications);
    }
    if (savePrefsBtn) {
      savePrefsBtn.addEventListener("click", function () {
        document.querySelectorAll("#prefList input[type=checkbox]").forEach(function (cb) {
          var idx = parseInt(cb.getAttribute("data-idx"), 10);
          var field = cb.getAttribute("data-field");
          if (prefs[idx]) prefs[idx][field] = cb.checked;
        });
        RoustoAPI.updateNotificationPreferences(prefs)
          .then(function () {
            RoustoToast("تم حفظ التفضيلات");
          })
          .catch(function (err) {
            RoustoToast(err.message, "error");
          });
      });
    }

    loadNotifications();
    loadPreferences();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
