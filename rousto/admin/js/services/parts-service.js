(function (global) {
  class PartsService {
    constructor(api) {
      this.api = api;
    }

    listParts() {
      return this.api.get("/admin/parts");
    }

    listWarrantyClaims() {
      return this.api.get("/admin/part-warranty-claims");
    }
  }

  global.PartsService = PartsService;
})(window);
