(function () {
  "use strict";

  // Language tabs (Français / English) on the blog post form.
  document.querySelectorAll("[data-lang-tabs]").forEach(function (tabs) {
    var buttons = tabs.querySelectorAll(".lang-tab-btn");
    var panels = document.querySelectorAll("[data-lang-panel]");
    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        var lang = button.dataset.lang;
        buttons.forEach(function (b) { b.classList.toggle("active", b === button); });
        panels.forEach(function (panel) {
          panel.hidden = panel.dataset.langPanel !== lang;
        });
      });
    });
  });

  // Dynamic "add another attachment" row for the blog attachments formset.
  var addButton = document.getElementById("add-attachment");
  if (addButton) {
    var container = document.getElementById("attachment-forms");
    var totalForms = document.getElementById("id_attachments-TOTAL_FORMS");
    var template = document.getElementById("empty-form-template");
    var maxForms = parseInt(addButton.dataset.maxForms, 10) || 10;

    addButton.addEventListener("click", function () {
      var currentCount = parseInt(totalForms.value, 10);
      if (currentCount >= maxForms) {
        return;
      }
      var html = template.innerHTML.replace(/__prefix__/g, currentCount);
      var wrapper = document.createElement("div");
      wrapper.innerHTML = html.trim();
      container.appendChild(wrapper.firstElementChild);
      totalForms.value = currentCount + 1;
      if (currentCount + 1 >= maxForms) {
        addButton.setAttribute("disabled", "disabled");
      }
    });
  }
})();
