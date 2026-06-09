const tabButtons = document.querySelectorAll(".tab-btn");
const phoneScreens = document.querySelectorAll(".phone-frame");
const timeline = document.querySelector("#order-timeline");

tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = button.dataset.screen;

    tabButtons.forEach((btn) => btn.classList.remove("active"));
    phoneScreens.forEach((screen) => screen.classList.remove("active"));

    button.classList.add("active");
    const selectedScreen = document.querySelector(`.phone-frame[data-screen="${target}"]`);
    if (selectedScreen) {
      selectedScreen.classList.add("active");
    }
  });
});

// Small loop to simulate order progress updates in hero card.
if (timeline) {
  const states = [
    ["done", "done", "active", ""],
    ["done", "done", "done", "active"],
    ["done", "done", "active", ""]
  ];
  let index = 0;

  setInterval(() => {
    const items = timeline.querySelectorAll("li");
    const currentState = states[index % states.length];

    items.forEach((item, itemIndex) => {
      item.classList.remove("done", "active");
      if (currentState[itemIndex]) {
        item.classList.add(currentState[itemIndex]);
      }
    });

    index += 1;
  }, 2600);
}
