/* Entry-portal behaviour: the particle field behind the tiles, and the sliding
 * doors played while the visitor enters the site.
 *
 * Both are written by hand rather than pulled from particles.js, jQuery and
 * GSAP, because the portal — like the rest of the site — loads nothing from a
 * third-party CDN. Everything here is progressive enhancement: the language
 * links are ordinary anchors that keep working without JavaScript, when the
 * visitor asks for reduced motion, or if an animation never fires.
 */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* ------------------------------------------------------------ particles */
  function startParticles(canvas) {
    var context = canvas.getContext("2d");
    if (!context) {
      return;
    }

    var COLOR = "#0056b3";
    var LINK_DISTANCE = 120;
    var AREA_PER_PARTICLE = 700 * 700 / 50; // ~50 particles over a 700x700 area
    var particles = [];
    var width = 0;
    var height = 0;
    var ratio = Math.min(window.devicePixelRatio || 1, 2);
    var frame = null;

    function resize() {
      var box = canvas.getBoundingClientRect();
      width = box.width;
      height = box.height;
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
      context.setTransform(ratio, 0, 0, ratio, 0, 0);

      var wanted = Math.max(12, Math.min(70, Math.round(width * height / AREA_PER_PARTICLE)));
      while (particles.length > wanted) {
        particles.pop();
      }
      while (particles.length < wanted) {
        particles.push(spawn());
      }
    }

    function spawn() {
      var angle = Math.random() * Math.PI * 2;
      var speed = 0.35 + Math.random() * 0.45;
      return {
        x: Math.random() * width,
        y: Math.random() * height,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        radius: 1 + Math.random() * 2,
        alpha: 0.12 + Math.random() * 0.2,
      };
    }

    function step() {
      context.clearRect(0, 0, width, height);

      var i;
      var j;
      for (i = 0; i < particles.length; i++) {
        var p = particles[i];
        p.x += p.vx;
        p.y += p.vy;

        // Wrap around the edges, the way the original field did.
        if (p.x < -10) { p.x = width + 10; }
        if (p.x > width + 10) { p.x = -10; }
        if (p.y < -10) { p.y = height + 10; }
        if (p.y > height + 10) { p.y = -10; }
      }

      context.strokeStyle = COLOR;
      context.lineWidth = 1;
      for (i = 0; i < particles.length; i++) {
        for (j = i + 1; j < particles.length; j++) {
          var dx = particles[i].x - particles[j].x;
          var dy = particles[i].y - particles[j].y;
          var distance = Math.sqrt(dx * dx + dy * dy);
          if (distance < LINK_DISTANCE) {
            context.globalAlpha = 0.2 * (1 - distance / LINK_DISTANCE);
            context.beginPath();
            context.moveTo(particles[i].x, particles[i].y);
            context.lineTo(particles[j].x, particles[j].y);
            context.stroke();
          }
        }
      }

      context.fillStyle = COLOR;
      for (i = 0; i < particles.length; i++) {
        context.globalAlpha = particles[i].alpha;
        context.beginPath();
        context.arc(particles[i].x, particles[i].y, particles[i].radius, 0, Math.PI * 2);
        context.fill();
      }

      context.globalAlpha = 1;
      frame = window.requestAnimationFrame(step);
    }

    var resizeTimer = null;
    window.addEventListener("resize", function () {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(resize, 150);
    });

    // Stop burning frames while the tab is in the background.
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) {
        if (frame !== null) {
          window.cancelAnimationFrame(frame);
          frame = null;
        }
      } else if (frame === null) {
        frame = window.requestAnimationFrame(step);
      }
    });

    resize();
    frame = window.requestAnimationFrame(step);
  }

  /* ---------------------------------------------------------- sliding doors */
  function wireDoors(wrapper, doors) {
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

        wrapper.classList.add("is-open");
        document.body.classList.add("no-scroll");

        // Next frame, so the panels animate from their closed position.
        window.requestAnimationFrame(function () {
          window.setTimeout(function () {
            wrapper.classList.add("is-parting");
          }, 500);
        });

        // Panels part (1.5s), the frame pulls away, then the screen fades out.
        window.setTimeout(function () { wrapper.classList.add("is-leaving"); }, 2100);
        window.setTimeout(function () { wrapper.classList.add("is-fading"); }, 3000);

        // Safety net: never trap the visitor behind the animation.
        window.setTimeout(go, 3400);
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var canvas = document.getElementById("particles-js");
    if (canvas && canvas.getContext && !reduceMotion.matches) {
      startParticles(canvas);
    }

    var wrapper = document.getElementById("doorWrapper");
    var doors = Array.prototype.slice.call(document.querySelectorAll("[data-door]"));
    if (wrapper && doors.length) {
      wireDoors(wrapper, doors);
    }
  });
})();
