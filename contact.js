// Contact page: a 911 GT3 RS drives off the email line and the address
// materialises in the dust it leaves behind. The address is assembled here at
// runtime so it never appears in the page source for scrapers to harvest.
(function () {
  "use strict";
  var item = document.getElementById("email-item");
  var slot = document.getElementById("email-text");
  if (!item || !slot) { return; }

  item.classList.add("is-armed");

  var codes = [110, 119, 104, 117, 108, 122, 104, 121, 53, 106, 122, 71, 110, 116, 104, 112, 115, 53, 106, 118, 116];
  var address = codes.map(function (c) { return String.fromCharCode(c - 7); }).join("");
  var link = document.createElement("a");
  link.href = "mailto:" + address;
  link.textContent = address;
  slot.textContent = "";
  slot.appendChild(link);

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    item.classList.add("is-revealed");
    return;
  }

  // Dust kicked up behind the rear wheel as the car launches.
  var dust = item.querySelector(".dust");
  for (var i = 0; i < 12; i++) {
    var t = i / 11;
    var puff = document.createElement("span");
    puff.style.setProperty("--x", (2 + t * 150 + (Math.random() * 16 - 8)).toFixed(0) + "px");
    puff.style.setProperty("--dx", (-(18 + Math.random() * 30)).toFixed(0) + "px");
    puff.style.setProperty("--dy", (-(22 + Math.random() * 34)).toFixed(0) + "px");
    puff.style.setProperty("--s", (1.8 + Math.random() * 1.4).toFixed(2));
    puff.style.animationDelay = (0.15 + t * 0.55).toFixed(2) + "s";
    puff.style.animationDuration = (1.5 + Math.random() * 0.8).toFixed(2) + "s";
    dust.appendChild(puff);
  }

  var started = false;
  function start() {
    if (started) { return; }
    started = true;
    item.classList.add("is-driving");
    setTimeout(function () { item.classList.add("is-done"); }, 3200);   // after the last dust puff has faded
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
