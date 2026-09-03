// Contact page: a 911 GT3 RS drives off the email line and the address
// materialises in the dust it leaves behind.
(function () {
  "use strict";
  var item = document.getElementById("email-item");
  if (!item) { return; }

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) { return; }
  item.classList.add("is-armed");

  // Dust kicked up behind the car along the whole length of the address, each
  // puff timed to the moment the car's tail passes it.
  var scale = parseFloat(getComputedStyle(item).getPropertyValue("--car-width")) / 168 || 1;
  var text = item.querySelector(".email-text");
  var stageLeft = 26;                                   // the stage starts 26px left of the text
  var span = (text ? text.getBoundingClientRect().width : 260) + stageLeft + 12;
  var distance = window.innerWidth + 80;                // matches translateX(calc(100vw + 80px))
  function passTime(x) {                                // drive easing: cubic-bezier(0.6, 0, 1, 0.45), 1.6s after a 0.3s hold
    var target = Math.min(x / distance, 0.999), lo = 0, hi = 1, s = 0.5, y;
    for (var k = 0; k < 30; k++) {
      s = (lo + hi) / 2;
      y = 3 * (1 - s) * s * s * 0.45 + s * s * s;
      if (y < target) { lo = s; } else { hi = s; }
    }
    var xb = 3 * (1 - s) * (1 - s) * s * 0.6 + 3 * (1 - s) * s * s + s * s * s;
    return 0.3 + 1.6 * xb;
  }
  var dust = item.querySelector(".dust");
  var count = 22;
  for (var i = 0; i < count; i++) {
    var x = Math.max(0, (i / (count - 1)) * span + (Math.random() * 14 - 7));
    var puff = document.createElement("span");
    puff.style.setProperty("--x", x.toFixed(1) + "px");
    puff.style.setProperty("--dx", (-(14 + Math.random() * 26) * scale).toFixed(1) + "px");
    puff.style.setProperty("--dy", (-(20 + Math.random() * 34) * scale).toFixed(1) + "px");
    puff.style.setProperty("--s", (1.9 + Math.random() * 1.4).toFixed(2));
    puff.style.animationDelay = (passTime(x) + 0.05).toFixed(2) + "s";
    puff.style.animationDuration = (2.1 + Math.random() * 1.1).toFixed(2) + "s";
    dust.appendChild(puff);
  }

  var started = false;
  function start() {
    if (started) { return; }
    started = true;
    item.classList.add("is-driving");
    setTimeout(function () { item.classList.add("is-done"); }, 5000);   // after the last dust puff has faded
    var seek = /^#t=([\d.]+)$/.exec(location.hash);   // #t=0.8 freezes the scene at 0.8s
    if (seek) {
      requestAnimationFrame(function () {
        document.getAnimations().forEach(function (a) { a.pause(); a.currentTime = parseFloat(seek[1]) * 1000; });
      });
    }
  }
  var body = item.querySelector(".car-body");
  if (body && body.decode) { body.decode().then(start, start); } else { start(); }
  setTimeout(start, 1500);
})();
