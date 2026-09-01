document.addEventListener("DOMContentLoaded", function () {
  // Auto-dismiss success alerts after a few seconds.
  document.querySelectorAll(".alert-success").forEach(function (alertEl) {
    setTimeout(function () {
      const alert = bootstrap.Alert.getOrCreateInstance(alertEl);
      alert.close();
    }, 6000);
  });
});
