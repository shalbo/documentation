/**
 * Admin payments module service.
 */
(function (global) {
  class PaymentService {
    constructor(api) {
      this.api = api;
    }

    getOverview() {
      return this.api.get("/admin/payments/overview");
    }

    listPendingWithdrawals() {
      return this.api.get("/admin/withdrawals?status=pending");
    }

    getAuditLog(limit = 30) {
      return this.api.get(`/admin/payments/audit?limit=${limit}`);
    }

    approveWithdrawal(id, { adminNote, markPaid = true } = {}) {
      return this.api.patch(`/admin/withdrawals/${id}`, {
        admin_note: adminNote || null,
        mark_paid: markPaid,
      });
    }
  }

  global.PaymentService = PaymentService;
})(window);
