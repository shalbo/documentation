(function (global) {
  "use strict";

  var STORAGE_KEY = "rousto_web_config";
  var DEFAULT_USER = "a0000000-0000-4000-8000-000000000001";

  function loadConfig() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
    } catch (_) {
      return {};
    }
  }

  function saveConfig(patch) {
    var current = loadConfig();
    var next = Object.assign({}, current, patch);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    return next;
  }

  var RoustoConfig = {
    STORAGE_KEY: STORAGE_KEY,
    load: loadConfig,
    save: saveConfig,
    get apiBase() {
      return (loadConfig().apiBase || "http://localhost:8000").replace(/\/$/, "");
    },
    get userId() {
      return loadConfig().userId || DEFAULT_USER;
    },
    get accessToken() {
      return loadConfig().accessToken || "";
    },
    get refreshToken() {
      return loadConfig().refreshToken || "";
    },
    get isLoggedIn() {
      return Boolean(loadConfig().accessToken);
    },
    set apiBase(value) {
      saveConfig({ apiBase: String(value || "").replace(/\/$/, "") });
    },
    set userId(value) {
      saveConfig({ userId: String(value || "").trim() });
    },
    set accessToken(value) {
      saveConfig({ accessToken: String(value || "").trim() });
    },
    set refreshToken(value) {
      saveConfig({ refreshToken: String(value || "").trim() });
    },
    clearAuth: function () {
      saveConfig({ accessToken: "", refreshToken: "", userId: "" });
    },
  };

  async function request(path, options) {
    options = options || {};
    var headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
    if (options.auth !== false) {
      if (RoustoConfig.accessToken) {
        headers.Authorization = "Bearer " + RoustoConfig.accessToken;
      } else {
        headers["X-User-Id"] = RoustoConfig.userId;
      }
    }
    var res = await fetch(RoustoConfig.apiBase + "/api/v1" + path, {
      method: options.method || "GET",
      headers: headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    var data = await res.json().catch(function () {
      return {};
    });
    if (!res.ok) {
      var msg = (data.error && data.error.message) || "خطأ " + res.status;
      throw new Error(msg);
    }
    return data;
  }

  var RoustoAPI = {
    health: function () {
      return request("/health", { auth: false });
    },
    getMe: function () {
      return request("/me");
    },
    authMe: function () {
      return request("/auth/me");
    },
    sendOtp: function (phone) {
      return request("/auth/otp/send", {
        method: "POST",
        auth: false,
        body: { phone: phone },
      });
    },
    verifyOtp: function (phone, code, requestId) {
      var body = { phone: phone, code: code };
      if (requestId) body.request_id = requestId;
      return request("/auth/otp/verify", {
        method: "POST",
        auth: false,
        body: body,
      });
    },
    refreshAuth: function () {
      return request("/auth/refresh", {
        method: "POST",
        auth: false,
        body: { refresh_token: RoustoConfig.refreshToken },
      });
    },
    logout: function () {
      var token = RoustoConfig.refreshToken;
      RoustoConfig.clearAuth();
      if (!token) return Promise.resolve({ data: { logged_out: true } });
      return request("/auth/logout", {
        method: "POST",
        auth: false,
        body: { refresh_token: token },
      });
    },
    getCategoriesTree: function () {
      return request("/categories/tree", { auth: false });
    },
    getLandingPage: function () {
      return request("/landing/page", { auth: false });
    },
    getLandingPricing: function () {
      return request("/landing/pricing", { auth: false });
    },
    getActiveBooking: function () {
      return request("/bookings/active");
    },
    listBookings: function () {
      return request("/bookings");
    },
    getVehicles: function () {
      return request("/me/vehicles");
    },
    getAddresses: function () {
      return request("/me/addresses");
    },
    getPaymentMethods: function () {
      return request("/me/payment-methods");
    },
    getLoyalty: function () {
      return request("/me/loyalty");
    },
    getMonetization: function () {
      return request("/me/monetization");
    },
    validatePromo: function (code, servicePrice) {
      return request("/promotions/validate", {
        method: "POST",
        body: { code: code, service_price_sar: servicePrice },
      });
    },
    createBooking: function (payload) {
      return request("/bookings", { method: "POST", body: payload });
    },
    getActiveDeliveryMap: function () {
      return request("/bookings/active/delivery-map");
    },
    getFaq: function () {
      return request("/support/faq", { auth: false });
    },
    listTickets: function () {
      return request("/support/tickets");
    },
    createTicket: function (payload) {
      return request("/support/tickets", { method: "POST", body: payload });
    },
    getTicket: function (id) {
      return request("/support/tickets/" + id);
    },
    replyTicket: function (id, message) {
      return request("/support/tickets/" + id + "/messages", {
        method: "POST",
        body: { message: message },
      });
    },
    getSecuritySummary: function () {
      return request("/me/security");
    },
    reportSecurity: function (description) {
      return request("/me/security/report", {
        method: "POST",
        body: { description: description },
      });
    },
    getMarketingBanners: function (placement) {
      var q = placement ? "?placement=" + encodeURIComponent(placement) : "";
      return request("/marketing/banners" + q, { auth: false });
    },
    getMarketingPartners: function () {
      return request("/marketing/partners", { auth: false });
    },
    subscribeNewsletter: function (email, source) {
      return request("/marketing/newsletter/subscribe", {
        method: "POST",
        auth: false,
        body: { email: email, source: source || "landing" },
      });
    },
    validateReferral: function (code) {
      return request("/marketing/referrals/validate?code=" + encodeURIComponent(code), {
        auth: false,
      });
    },
    getMyReferral: function () {
      return request("/me/referral");
    },
  };

  function showToast(message, type) {
    var el = document.getElementById("portalToast");
    if (!el) return;
    el.textContent = message;
    el.className = "portal-toast show" + (type ? " " + type : "");
    setTimeout(function () {
      el.classList.remove("show");
    }, 2800);
  }

  global.RoustoConfig = RoustoConfig;
  global.RoustoAPI = RoustoAPI;
  global.RoustoToast = showToast;
})(window);
