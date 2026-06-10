(function () {
  "use strict";

  var state = { requestId: null, phone: "" };

  function $(id) {
    return document.getElementById(id);
  }

  $("phoneForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    state.phone = $("phone").value.trim();
    try {
      var res = await RoustoAPI.sendOtp(state.phone);
      state.requestId = res.data.request_id;
      $("otpForm").style.display = "block";
      if (res.meta && res.meta.dev_otp) {
        $("devOtpHint").style.display = "block";
        $("devOtpHint").textContent = "وضع التطوير — الرمز: " + res.meta.dev_otp;
        $("otpCode").value = res.meta.dev_otp;
      }
      RoustoToast("تم إرسال الرمز");
    } catch (err) {
      RoustoToast(err.message, "error");
    }
  });

  $("otpForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      var res = await RoustoAPI.verifyOtp(
        state.phone,
        $("otpCode").value.trim(),
        state.requestId
      );
      var data = res.data;
      RoustoConfig.save({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        userId: data.principal.user.id,
      });
      RoustoToast("مرحباً " + data.principal.user.full_name);
      setTimeout(function () {
        window.location.href = "dashboard.html";
      }, 800);
    } catch (err) {
      RoustoToast(err.message, "error");
    }
  });
})();
