(function () {
  const tabButtons = document.querySelectorAll("[data-view]");
  const panels = document.querySelectorAll("[data-panel]");

  function activatePanel(view) {
    tabButtons.forEach((button) => {
      const isActive = button.dataset.view === view;
      button.classList.toggle("is-active", isActive);
      button.setAttribute("aria-selected", String(isActive));
    });

    panels.forEach((panel) => {
      const isActive = panel.dataset.panel === view;
      panel.classList.toggle("is-active", isActive);
    });
  }

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activatePanel(button.dataset.view);
      const target = document.getElementById(button.dataset.view);

      if (target) {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });
})();
