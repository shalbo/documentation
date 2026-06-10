/**
 * Vendor wallet module service.
 */
(function (global) {
  class VendorWalletService {
    constructor(api) {
      this.api = api;
    }

    getWallet() {
      return this.api.get("/vendor/wallet");
    }

    requestWithdrawal({ amountLyd, bankName, iban, note }) {
      return this.api.post("/vendor/wallet/withdraw", {
        amount_lyd: amountLyd,
        bank_name: bankName || null,
        iban: iban || null,
        note: note || null,
      });
    }
  }

  global.VendorWalletService = VendorWalletService;
})(window);
