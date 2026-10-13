(function () {
  var doc = document.documentElement;

  // Countdown to doors (7 PM CDT, Oct 31).
  var target = Date.parse('2026-11-01T00:00:00Z');
  var close = Date.parse('2026-11-01T13:00:00Z');
  var cd = document.querySelector('.countdown');
  var label = document.querySelector('.countdown-label');
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function tick() {
    if (!cd) return;
    var now = Date.now(), diff = target - now;
    if (diff <= 0) {
      cd.hidden = true;
      if (label) label.textContent = now < close ? 'The veil is open.' : 'Until next Halloween.';
      return;
    }
    var s = Math.floor(diff / 1000);
    var parts = { d: Math.floor(s / 86400), h: Math.floor(s % 86400 / 3600), m: Math.floor(s % 3600 / 60), s: s % 60 };
    for (var k in parts) {
      var el = cd.querySelector('[data-u="' + k + '"]');
      if (el) el.textContent = k === 'd' ? parts[k] : pad(parts[k]);
    }
    setTimeout(tick, 1000 - (now % 1000));
  }
  tick();

  // Navigation: solid after the hero, mobile menu.
  var nav = document.getElementById('nav');
  var hero = document.querySelector('.hero');
  var sticky = document.querySelector('.sticky');
  var tickets = document.getElementById('tickets');
  var closing = document.querySelector('.closing');
  if (nav && hero && 'IntersectionObserver' in window) {
    var heroOn = true, ticketsOn = false, closingOn = false;
    var sync = function () {
      nav.classList.toggle('solid', !heroOn);
      doc.classList.toggle('past-hero', !heroOn);
      if (sticky) sticky.classList.toggle('show', !heroOn && !ticketsOn && !closingOn);
    };
    new IntersectionObserver(function (e) { heroOn = e[0].intersectionRatio > 0.15; sync(); }, { threshold: [0, 0.15, 1] }).observe(hero);
    if (tickets) new IntersectionObserver(function (e) { ticketsOn = e[0].isIntersecting; sync(); }, { threshold: 0.1 }).observe(tickets);
    if (closing) new IntersectionObserver(function (e) { closingOn = e[0].isIntersecting; sync(); }).observe(closing);
  }
  // Header hides while scrolling down and returns on any scroll up.
  if (nav) {
    var lastY = window.scrollY, ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function () {
        var y = window.scrollY, dy = y - lastY;
        if (doc.classList.contains('menu-open') || y < 80) nav.classList.remove('nav-hidden');
        else if (dy > 6) nav.classList.add('nav-hidden');
        else if (dy < -6) nav.classList.remove('nav-hidden');
        if (Math.abs(dy) > 6) lastY = y;
        ticking = false;
      });
    }, { passive: true });
    nav.addEventListener('focusin', function () { nav.classList.remove('nav-hidden'); });
  }
  var btn = document.querySelector('.menu-btn');
  var menu = document.getElementById('menu');
  function setMenu(open) {
    if (!btn || !menu) return;
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    menu.hidden = !open;
    doc.classList.toggle('menu-open', open);
  }
  if (btn) btn.addEventListener('click', function () { setMenu(btn.getAttribute('aria-expanded') !== 'true'); });
  if (menu) menu.addEventListener('click', function (ev) { if (ev.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') setMenu(false); });

  // Gentle reveal for sections as they arrive. Content is visible without JS.
  if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    doc.classList.add('reveal-ready');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -10% 0px' });
    document.querySelectorAll('main > section').forEach(function (s) { io.observe(s); });
  }

  // The recap video loads only when tapped.
  var video = document.querySelector('.video button');
  if (video) {
    video.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + video.getAttribute('data-id') + '?autoplay=1&rel=0';
      f.title = 'Halloween 2025 recap';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      video.replaceWith(f);
    });
  }

  // Pinterest board: sized to its frame, loaded only when the costume section comes near.
  var pin = document.getElementById('pin-frame');
  if (pin) {
    var loadPin = function () {
      var a = pin.querySelector('[data-pin-do]');
      if (!a || pin.dataset.loaded) return;
      pin.dataset.loaded = '1';
      a.setAttribute('data-pin-board-width', String(Math.max(280, Math.min(1000, pin.clientWidth - 32))));
      var s = document.createElement('script');
      s.async = true; s.src = 'https://assets.pinterest.com/js/pinit.js';
      document.body.appendChild(s);
    };
    if ('IntersectionObserver' in window) {
      var pio = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { loadPin(); pio.disconnect(); } }, { rootMargin: '600px 0px' });
      pio.observe(pin);
    } else { loadPin(); }
  }

  // Etsy photos: fall back to the full-size image once, then show the dark tile.
  document.querySelectorAll('.etsy-img img').forEach(function (img) {
    img.addEventListener('error', function () {
      var full = img.getAttribute('data-full');
      if (full && img.src !== full) { img.src = full; } else { img.remove(); }
    });
  });

  // Only one FAQ answer open at a time keeps the list scannable.
  var faqs = document.querySelectorAll('.faq-list details');
  faqs.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (d.open) faqs.forEach(function (o) { if (o !== d) o.open = false; });
    });
  });
})();
