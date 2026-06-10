/** Shared vendor store open/closed toggle — updates local state without reload. */

window.VendorStoreStatus = (function () {
  const state = { isActive: true, loading: false };

  function getEls(prefix = "") {
    const p = prefix ? `${prefix}-` : "";
    return {
      wrap: document.getElementById(`${p}storeStatusWrap`),
      toggle: document.getElementById(`${p}storeStatusToggle`),
      label: document.getElementById(`${p}storeStatusLabel`),
      notice: document.getElementById(`${p}storeClosedNotice`),
    };
  }

  function render(prefix = "") {
    const { wrap, toggle, label, notice } = getEls(prefix);
    if (!wrap) return;
    wrap.classList.toggle("store-open", state.isActive);
    wrap.classList.toggle("store-closed", !state.isActive);
    if (toggle) toggle.checked = state.isActive;
    if (label) {
      label.innerHTML = state.isActive
        ? '<span class="status-dot ping"></span> المحل يستقبل طلبات'
        : "المتجر مغلق مؤقتاً";
    }
    if (notice) {
      notice.textContent = state.isActive
        ? ""
        : "بضاعتك مخفية الآن عن الزبائن";
      notice.style.display = state.isActive ? "none" : "block";
    }
  }

  function setActive(value, prefix = "") {
    state.isActive = Boolean(value);
    render(prefix);
  }

  async function load(vendorApi, prefix = "") {
    try {
      const body = await vendorApi("/vendor/me");
      setActive(body.data.is_active !== false, prefix);
    } catch (_) {
      setActive(true, prefix);
    }
  }

  async function toggle(vendorApi, toast, prefix = "") {
    if (state.loading) return;
    state.loading = true;
    const { toggle: el } = getEls(prefix);
    if (el) el.disabled = true;
    try {
      const body = await vendorApi("/vendor/status/toggle", { method: "PATCH" });
      setActive(body.data.is_active, prefix);
      if (toast) toast(body.data.message_ar);
    } catch (err) {
      render(prefix);
      if (toast) toast(err.message, true);
    } finally {
      state.loading = false;
      if (el) el.disabled = false;
    }
  }

  function bind(vendorApi, toast, prefix = "") {
    const { toggle: el } = getEls(prefix);
    if (!el) return;
    el.addEventListener("change", () => {
      toggle(vendorApi, toast, prefix);
    });
    load(vendorApi, prefix);
  }

  return { state, setActive, load, toggle, bind, render };
})();
