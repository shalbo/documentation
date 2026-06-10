(function (global) {
  class NotificationsService {
    constructor(api) {
      this.api = api;
    }

    getAnalytics() {
      return this.api.get("/admin/notifications/analytics");
    }

    listTemplates() {
      return this.api.get("/admin/notifications/templates");
    }

    broadcast(payload) {
      return this.api.post("/admin/notifications/broadcast", payload);
    }

    sendTest(payload) {
      return this.api.post("/admin/notifications/send", payload);
    }

    searchUsers(query) {
      return this.api.get(`/admin/notifications/users/search?q=${encodeURIComponent(query)}`);
    }
  }

  global.NotificationsService = NotificationsService;
})(window);
