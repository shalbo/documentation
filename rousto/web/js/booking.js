(function () {
  "use strict";

  var state = {
    services: [],
    selectedId: null,
    price: 0,
    discount: 0,
    total: 0,
  };

  function $(id) {
    return document.getElementById(id);
  }

  function formatDinar(amount) {
    var n = Number(amount);
    return (n % 1 === 0 ? n : n.toFixed(2)) + " دينار";
  }

  function allServices(tree) {
    var list = [];
    tree.forEach(function (cat) {
      (cat.services || []).forEach(function (s) {
        if (!list.some(function (x) {
          return x.id === s.id;
        })) {
          list.push(s);
        }
      });
    });
    return list.sort(function (a, b) {
      return a.name_ar.localeCompare(b.name_ar, "ar");
    });
  }

  function renderServices() {
    var el = $("servicesList");
    if (!state.services.length) {
      el.innerHTML = "<p class='portal-empty'>لا توجد خدمات</p>";
      return;
    }
    el.innerHTML = state.services
      .map(function (s) {
        var checked = state.selectedId === s.id ? " checked" : "";
        var sel = state.selectedId === s.id ? " selected" : "";
        return (
          '<label class="portal-service-option' + sel + '">' +
          '<input type="radio" name="service" value="' + s.id + '"' + checked + " />" +
          "<div><b>" + s.name_ar + "</b><br>" +
          "<small>" + (s.subtitle_ar || "") + " · " + formatDinar(s.price_sar) + "</small></div>" +
          "</label>"
        );
      })
      .join("");

    el.querySelectorAll('input[name="service"]').forEach(function (input) {
      input.addEventListener("change", function () {
        state.selectedId = input.value;
        var svc = state.services.find(function (s) {
          return s.id === state.selectedId;
        });
        state.price = svc ? svc.price_sar : 0;
        renderServices();
        updatePromo();
      });
    });
  }

  function fillSelect(id, items, render) {
    var el = $(id);
    el.innerHTML = items.map(render).join("");
  }

  async function updatePromo() {
    var code = $("promoCode").value.trim();
    $("sumService").textContent = formatDinar(state.price);
    if (!code || !state.price) {
      state.discount = 0;
      state.total = state.price;
      $("sumDiscount").textContent = "0 دينار";
      $("sumTotal").textContent = formatDinar(state.total);
      return;
    }
    try {
      var res = await RoustoAPI.validatePromo(code, state.price);
      var data = res.data;
      state.discount = data.discount_sar || 0;
      state.total = data.total_sar || state.price;
      $("sumDiscount").textContent = "- " + formatDinar(state.discount);
      $("sumTotal").textContent = formatDinar(state.total);
    } catch (_) {
      state.discount = 0;
      state.total = state.price;
      $("sumDiscount").textContent = "0 دينار";
      $("sumTotal").textContent = formatDinar(state.total);
    }
  }

  async function load() {
    try {
      var treeRes = await RoustoAPI.getCategoriesTree();
      state.services = allServices(treeRes.data || []);
      if (!state.selectedId && state.services.length) {
        state.selectedId = state.services[0].id;
        state.price = state.services[0].price_sar;
      }
      var params = new URLSearchParams(window.location.search);
      var slug = params.get("service");
      if (slug) {
        var match = state.services.find(function (s) {
          return s.slug === slug;
        });
        if (match) {
          state.selectedId = match.id;
          state.price = match.price_sar;
        }
      }
      renderServices();

      var vehiclesRes = await RoustoAPI.getVehicles();
      fillSelect("vehicleSelect", vehiclesRes.data || [], function (v) {
        return (
          '<option value="' + v.id + '">' +
          (v.display_name || v.make + " " + v.model) +
          " · " + v.plate_number +
          "</option>"
        );
      });

      var addressesRes = await RoustoAPI.getAddresses();
      fillSelect("addressSelect", addressesRes.data || [], function (a) {
        return '<option value="' + a.id + '">' + a.label + " — " + a.district + "، " + a.city + "</option>";
      });

      var paymentsRes = await RoustoAPI.getPaymentMethods();
      fillSelect("paymentSelect", paymentsRes.data || [], function (p) {
        return '<option value="' + p.id + '">' + p.label_ar + "</option>";
      });

      var tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      tomorrow.setMinutes(0, 0, 0);
      $("scheduledAt").value = tomorrow.toISOString().slice(0, 16);

      $("promoCode").addEventListener("input", updatePromo);
      await updatePromo();
    } catch (err) {
      $("servicesList").innerHTML = "<p class='portal-empty'>" + err.message + "</p>";
      RoustoToast(err.message, "error");
    }
  }

  $("bookingForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    if (!state.selectedId) {
      RoustoToast("اختر خدمة", "error");
      return;
    }
    $("submitBtn").disabled = true;
    try {
      var res = await RoustoAPI.createBooking({
        service_id: state.selectedId,
        vehicle_id: $("vehicleSelect").value,
        address_id: $("addressSelect").value,
        payment_method_id: $("paymentSelect").value || null,
        promotion_code: $("promoCode").value.trim() || null,
        scheduled_at: new Date($("scheduledAt").value).toISOString(),
        notes: $("notes").value.trim() || null,
      });
      RoustoToast("تم الحجز: " + (res.data && res.data.reference || "نجاح"));
      setTimeout(function () {
        window.location.href = "dashboard.html";
      }, 1200);
    } catch (err) {
      RoustoToast(err.message, "error");
    } finally {
      $("submitBtn").disabled = false;
    }
  });

  window.onRoustoConfigSaved = load;
  load();
})();
