/**
 * Injects Rousto logo into admin/vendor topbars without stretching.
 */
(function () {
  const LOGO_SRC = "static/images/logo.png";

  function injectBrand() {
    document.querySelectorAll("header.topbar").forEach((header) => {
      const titleBlock = header.querySelector(":scope > div:first-child");
      if (!titleBlock || titleBlock.querySelector(".brand-logo")) return;

      const h1 = titleBlock.querySelector("h1");
      const p = titleBlock.querySelector("p");
      const brand = document.createElement("div");
      brand.className = "topbar-brand";

      const img = document.createElement("img");
      img.src = LOGO_SRC;
      img.alt = "Rousto";
      img.className = "brand-logo";
      img.width = 120;
      img.height = 46;
      img.loading = "eager";
      brand.appendChild(img);

      const text = document.createElement("div");
      text.className = "topbar-brand-text";
      if (h1) text.appendChild(h1);
      if (p) text.appendChild(p);
      brand.appendChild(text);

      titleBlock.replaceChildren(brand);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectBrand);
  } else {
    injectBrand();
  }
})();
