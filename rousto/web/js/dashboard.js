(function () {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function renderActive(booking) {
    var el = $("activeBooking");
    if (!booking) {
      el.className = "portal-empty";
      el.innerHTML = "لا يوجد حجز نشط حالياً. <a href='booking.html'>احجز الآن</a>";
      return;
    }
    el.className = "";
    el.innerHTML =
      '<div class="portal-list-item">' +
      "<div><b>" + (booking.service && booking.service.name_ar || "خدمة") + "</b><br>" +
      "<small>" + booking.reference + " · " + booking.status_label_ar + "</small></div>" +
      '<span class="portal-pill live">نشط</span></div>' +
      '<div class="portal-actions">' +
      '<a href="delivery-map.html" class="btn btn-primary btn-sm">تتبّع</a>' +
      '<a href="account.html" class="btn btn-ghost btn-sm">تفاصيل</a>' +
      "</div>";
  }

  async function load() {
    try {
      var meRes = await RoustoAPI.getMe();
      var user = meRes.data;
      $("welcomeHero").innerHTML =
        "<h1>مرحباً " + user.full_name + " 👋</h1>" +
        "<p>" + user.email + "</p>";
      $("statServices").textContent = (user.stats && user.stats.services_count) || 0;
      $("statVehicles").textContent = (user.stats && user.stats.vehicles_count) || 0;
      $("statPoints").textContent = user.loyalty_points || 0;

      var activeRes = await RoustoAPI.getActiveBooking();
      renderActive(activeRes.data);
    } catch (err) {
      $("activeBooking").className = "portal-empty";
      $("activeBooking").textContent = err.message || "تعذّر تحميل البيانات";
      RoustoToast(err.message || "خطأ في الاتصال", "error");
    }
  }

  window.onRoustoConfigSaved = load;
  load();
})();
