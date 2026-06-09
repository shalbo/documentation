(function () {
  "use strict";

  function $(id) {
    return document.getElementById(id);
  }

  function formatDinar(amount) {
    var n = Number(amount);
    return (n % 1 === 0 ? n : n.toFixed(2)) + " دينار";
  }

  async function load() {
    try {
      var meRes = await RoustoAPI.getMe();
      var user = meRes.data;
      $("profileHero").innerHTML =
        "<h1>" + user.full_name + "</h1>" +
        "<p>" + user.email + " · " + (user.phone || "") + "</p>";

      $("profileInfo").innerHTML =
        "<p><b>الاسم:</b> " + user.full_name + "</p>" +
        "<p><b>البريد:</b> " + user.email + "</p>" +
        "<p><b>الجوال:</b> " + (user.phone || "—") + "</p>" +
        "<p><b>النقاط:</b> " + (user.loyalty_points || 0) + "</p>";

      var monRes = await RoustoAPI.getMonetization();
      var mon = monRes.data || {};
      var membership = mon.membership || {};
      var loyalty = mon.loyalty || {};
      $("loyaltyInfo").innerHTML =
        "<p><b>الخطة:</b> " + (membership.plan_name_ar || "مجاني") + "</p>" +
        "<p><b>الخصم:</b> " + (membership.discount_percent || 0) + "٪</p>" +
        "<p><b>رصيد النقاط:</b> " + (loyalty.balance || 0) + "</p>" +
        "<p><b>توفير تراكمي:</b> " + formatDinar(mon.lifetime_savings_sar || 0) + "</p>";

      var vehiclesRes = await RoustoAPI.getVehicles();
      var vehicles = vehiclesRes.data || [];
      $("vehiclesList").innerHTML = vehicles.length
        ? vehicles
            .map(function (v) {
              return (
                '<div class="portal-list-item"><div><b>' +
                (v.display_name || v.make + " " + v.model) +
                "</b><br><small>" + v.plate_number + "</small></div>" +
                (v.is_default ? '<span class="portal-pill">افتراضية</span>' : "") +
                "</div>"
              );
            })
            .join("")
        : "<p class='portal-empty'>لا توجد سيارات</p>";

      var bookingsRes = await RoustoAPI.listBookings();
      var bookings = bookingsRes.data || [];
      $("bookingsList").innerHTML = bookings.length
        ? bookings
            .map(function (b) {
              var serviceName = (b.service && b.service.name_ar) || "خدمة";
              return (
                '<div class="portal-list-item"><div><b>' + serviceName + "</b><br>" +
                "<small>" + b.reference + " · " + b.status_label_ar + "</small></div>" +
                "<span>" + formatDinar(b.total_sar || b.service_price_sar || 0) + "</span></div>"
              );
            })
            .join("")
        : "<p class='portal-empty'>لا توجد طلبات بعد</p>";
    } catch (err) {
      $("profileInfo").textContent = err.message;
      RoustoToast(err.message, "error");
    }
  }

  window.onRoustoConfigSaved = load;
  load();
})();
