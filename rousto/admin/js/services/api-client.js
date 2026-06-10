/**
 * Shared Rousto admin API client — unified JSON envelope handling.
 * Usage: const api = RoustoApiClient.createAdminClient({ storageKey, getConfig, saveConfig });
 */
(function (global) {
  const API_PREFIX = "/api/v1";

  function parseError(body, status) {
    if (body?.error?.message) return body.error.message;
    if (body?.detail?.message) return body.detail.message;
    if (typeof body?.detail === "string") return body.detail;
    return `خطأ ${status}`;
  }

  class RoustoApiClient {
    constructor({ apiBase, headers = {} }) {
      this.apiBase = (apiBase || "http://localhost:8000").replace(/\/$/, "");
      this.headers = { "Content-Type": "application/json", ...headers };
    }

    async request(path, options = {}) {
      const res = await fetch(`${this.apiBase}${API_PREFIX}${path}`, {
        ...options,
        headers: { ...this.headers, ...(options.headers || {}) },
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(parseError(body, res.status));
      if (body.success === false) throw new Error(parseError(body, res.status));
      return body;
    }

    get(path) {
      return this.request(path);
    }

    post(path, payload) {
      return this.request(path, { method: "POST", body: JSON.stringify(payload) });
    }

    patch(path, payload) {
      return this.request(path, { method: "PATCH", body: JSON.stringify(payload) });
    }

    static createAdminClient({ getApiBase, getAdminKey, onConfigSave }) {
      const apiBase = getApiBase();
      const adminKey = getAdminKey();
      if (onConfigSave) onConfigSave({ apiBase, adminKey });
      return new RoustoApiClient({
        apiBase,
        headers: { "X-Admin-Key": adminKey },
      });
    }

    static createVendorClient({ getApiBase, getVendorId, onConfigSave }) {
      const apiBase = getApiBase();
      const vendorId = getVendorId();
      if (onConfigSave) onConfigSave({ apiBase, vendorId });
      return new RoustoApiClient({
        apiBase,
        headers: { "X-Vendor-Id": vendorId },
      });
    }
  }

  global.RoustoApiClient = RoustoApiClient;
})(window);
