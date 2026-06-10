(function (global) {
  class VendorPartsService {
    constructor(api) {
      this.api = api;
    }

    getTier() {
      return this.api.get("/vendor/parts/tier");
    }

    listCategoryRoots() {
      return this.api.get("/vendor/parts/categories/roots");
    }

    listCategoryChildren(parentId) {
      return this.api.get(`/vendor/parts/categories/${parentId}/children`);
    }

    createProduct(payload) {
      return this.api.post("/vendor/parts", payload);
    }

    getBulkTemplate() {
      return this.api.get("/vendor/parts/bulk-upload/template");
    }
  }

  global.VendorPartsService = VendorPartsService;
})(window);
