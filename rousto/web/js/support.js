(function () {
  "use strict";

  var state = { selectedTicketId: null };

  function $(id) {
    return document.getElementById(id);
  }

  function renderFaq(items) {
    $("faqList").innerHTML = items.length
      ? items
          .map(function (f) {
            return (
              '<div class="faq-item"><h3>' + f.question_ar + "</h3><p>" + f.answer_ar + "</p></div>"
            );
          })
          .join("")
      : "<p class='portal-empty'>لا توجد أسئلة</p>";
  }

  function renderTickets(tickets) {
    $("ticketList").innerHTML = tickets.length
      ? tickets
          .map(function (t) {
            return (
              '<div class="ticket-card" data-id="' + t.id + '">' +
              "<b>" + t.reference + "</b> · " + t.status_label_ar + "<br>" +
              "<small>" + t.subject + "</small></div>"
            );
          })
          .join("")
      : "<p class='portal-empty'>لا توجد تذاكر</p>";
  }

  function renderTicketDetail(ticket) {
    state.selectedTicketId = ticket.id;
    $("ticketDetail").style.display = "block";
    $("detailSubject").textContent = ticket.reference + " — " + ticket.subject;
    $("messages").innerHTML = (ticket.messages || [])
      .map(function (m) {
        return (
          '<div class="msg ' + m.author_type + '"><b>' + m.author_label + "</b><br>" + m.message + "</div>"
        );
      })
      .join("");
  }

  async function loadAll() {
    var faq = await RoustoAPI.getFaq();
    var tickets = await RoustoAPI.listTickets();
    var security = await RoustoAPI.getSecuritySummary();
    renderFaq(faq.data || []);
    renderTickets(tickets.data || []);
    $("securitySummary").textContent =
      "تذاكر مفتوحة: " + security.data.open_tickets_count +
      " · تنبيهات الدخول: " +
      (security.data.login_alerts_enabled ? "مفعّلة" : "معطّلة");
  }

  $("refreshBtn").addEventListener("click", function () {
    loadAll()
      .then(function () {
        RoustoToast("تم التحديث");
      })
      .catch(function (e) {
        RoustoToast(e.message, "error");
      });
  });

  $("ticketForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      var body = await RoustoAPI.createTicket({
        category: $("category").value,
        priority: $("priority").value,
        subject: $("subject").value.trim(),
        message: $("message").value.trim(),
      });
      RoustoToast("تم إنشاء " + body.data.reference);
      e.target.reset();
      await loadAll();
      renderTicketDetail(body.data);
    } catch (err) {
      RoustoToast(err.message, "error");
    }
  });

  $("ticketList").addEventListener("click", async function (e) {
    var card = e.target.closest("[data-id]");
    if (!card) return;
    try {
      var body = await RoustoAPI.getTicket(card.dataset.id);
      renderTicketDetail(body.data);
    } catch (err) {
      RoustoToast(err.message, "error");
    }
  });

  $("replyForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    if (!state.selectedTicketId) return;
    try {
      var body = await RoustoAPI.replyTicket(
        state.selectedTicketId,
        $("replyMessage").value.trim()
      );
      renderTicketDetail(body.data);
      $("replyMessage").value = "";
      RoustoToast("تم إرسال الرد");
    } catch (err) {
      RoustoToast(err.message, "error");
    }
  });

  $("reportForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      await RoustoAPI.reportSecurity($("reportDesc").value.trim());
      $("reportDesc").value = "";
      RoustoToast("تم تسجيل البلاغ");
      await loadAll();
    } catch (err) {
      RoustoToast(err.message, "error");
    }
  });

  window.onRoustoConfigSaved = loadAll;
  loadAll().catch(function () {});
})();
