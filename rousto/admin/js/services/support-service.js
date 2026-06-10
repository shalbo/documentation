(function (global) {
  class SupportService {
    constructor(api) {
      this.api = api;
    }

    listTickets(status) {
      const q = status ? `?status=${encodeURIComponent(status)}` : "";
      return this.api.get(`/admin/support/tickets${q}`);
    }

    getTicket(id) {
      return this.api.get(`/admin/support/tickets/${id}`);
    }

    reply(id, { message, status }) {
      return this.api.post(`/admin/support/tickets/${id}/reply`, {
        message,
        status: status || null,
      });
    }

    updateTicket(id, payload) {
      return this.api.patch(`/admin/support/tickets/${id}`, payload);
    }
  }

  global.SupportService = SupportService;
})(window);
