document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss success alerts after a few seconds.
  document.querySelectorAll(".alert-success").forEach(function (alertEl) {
    setTimeout(function () {
      const alert = bootstrap.Alert.getOrCreateInstance(alertEl);
      alert.close();
    }, 6000);
  });

  // Nested "Directions" flyout in the main navbar: desktop shows it on
  // hover (pure CSS), but the collapsed mobile menu needs a click to open
  // it since there is no hover there.
  document.querySelectorAll(".dropdown-submenu > .dropdown-toggle").forEach(function (toggle) {
    toggle.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      const submenu = toggle.nextElementSibling;
      const isShown = submenu.classList.contains("show");
      document.querySelectorAll(".dropdown-submenu > .dropdown-menu.show").forEach(function (menu) {
        menu.classList.remove("show");
      });
      if (!isShown) {
        submenu.classList.add("show");
      }
    });
  });
});
