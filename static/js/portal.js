/* Entry-portal door transition.
 *
 * Clicking one of the two language doors slides a pair of panels apart before
 * the browser navigates, which makes the jump from the portal into the site
 * feel deliberate. It is progressive enhancement only: the links are ordinary
 * anchors, so they keep working without JavaScript, when the visitor asks for
 * reduced motion, or if the transition never fires. */
(function () {
  "use strict";

  var overlay = document.getElementById("doorOverlay");
  var doors = document.querySelectorAll("[data-door]");
  if (!overlay || !doors.length) {
    return;
  }

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  doors.forEach(function (door) {
    door.addEventListener("click", function (event) {
      // Let modified clicks (new tab, new window, download) behave normally.
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) {
        return;
      }
      if (reduceMotion.matches) {
        return;
      }

      event.preventDefault();
      var target = door.getAttribute("href");
      var navigated = false;

      function go() {
        if (!navigated) {
          navigated = true;
          window.location.href = target;
        }
      }

      overlay.classList.add("is-open");
      // Next frame, so the panels animate from their closed position.
      window.requestAnimationFrame(function () {
        overlay.classList.add("is-parting");
      });

      overlay.querySelector(".door-panel.right").addEventListener("transitionend", go, { once: true });
      // Safety net: never trap the visitor behind the animation.
      window.setTimeout(go, 1400);
    });
  });
})();
