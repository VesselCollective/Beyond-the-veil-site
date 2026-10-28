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

// Live NWS forecast for HAVAN (Party Guide). Data: api.weather.gov (CORS-enabled, no key).
(function () {
  var box = document.querySelector('.wx');
  if (!box || !window.fetch || !window.Promise) return;
  var body = box.querySelector('.wx-body'), upd = box.querySelector('.wx-updated');
  var tabs = box.querySelectorAll('[data-view]');
  var TZ = 'America/Chicago';
  var START = Date.parse('2026-10-31T23:00:00Z'); // 6 PM CDT Oct 31
  var END = Date.parse('2026-11-01T14:00:00Z');   // 8 AM CST Nov 1 (clocks fall back at 2 AM)
  var hourly = null, week = null, view = 'night', sel = 0, failed = false;

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function get(u, tries) {
    return fetch(u).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .catch(function (err) { if ((tries || 0) < 1) return new Promise(function (ok) { setTimeout(ok, 1200); }).then(function () { return get(u, 1); }); throw err; });
  }
  function hr(t) { return new Date(t).toLocaleTimeString('en-US', { hour: 'numeric', timeZone: TZ }); }
  function pop(p) { return p.probabilityOfPrecipitation && p.probabilityOfPrecipitation.value != null ? p.probabilityOfPrecipitation.value : 0; }
  function mph(p) { var m = String(p.windSpeed || '').match(/\d+/g); return m ? Math.max.apply(null, m.map(Number)) : 0; }
  function sym(p) {
    var t = String(p.shortForecast || '').toLowerCase(), day = p.isDaytime;
    var s = /thunder|t-storm/.test(t) ? '⛈' : /rain|shower|drizzle/.test(t) ? '☔' : /fog|haze|smoke/.test(t) ? '≈'
      : /mostly cloudy|cloudy|overcast/.test(t) && !/partly/.test(t) ? '☁' : /partly|mostly sunny|mostly clear/.test(t) ? (day ? '⛅' : '☾')
      : day ? '☀' : '☾';
    return s + '︎';
  }

  function nightView() {
    var hrs = hourly.filter(function (p) { var s = Date.parse(p.startTime); return s >= START && s < END; });
    if (!hrs.length) {
      var last = hourly.length ? Date.parse(hourly[hourly.length - 1].endTime) : 0;
      return '<p class="wx-msg">' + (Date.now() > END ? 'The party has passed. See you beyond the veil next year.'
        : last < START ? 'The hour-by-hour forecast for party night appears about six days out. Check the 7-day view for now.'
        : 'Hourly forecast unavailable right now.') + '</p>';
    }
    if (sel >= hrs.length) sel = 0;
    var lo = Math.min.apply(null, hrs.map(function (p) { return p.temperature; }));
    var hi = Math.max.apply(null, hrs.map(function (p) { return p.temperature; }));
    var rain = Math.max.apply(null, hrs.map(pop));
    var wind = Math.max.apply(null, hrs.map(mph));
    var u = hrs[0].temperatureUnit || 'F';
    var stats = '<div class="wx-stats">'
      + '<div><b>' + lo + '°–' + hi + '°' + esc(u) + '</b><small>Temperature</small></div>'
      + '<div><b>' + rain + '%</b><small>Rain chance</small></div>'
      + '<div><b>' + wind + ' mph</b><small>Wind</small></div></div>';
    var strip = '<div class="wx-strip" role="listbox" aria-label="Hourly forecast, Oct 31 to Nov 1">' + hrs.map(function (p, i) {
      var r = pop(p);
      return '<button type="button" role="option" class="wx-hour' + (r >= 40 ? ' wet' : '') + '" aria-selected="' + (i === sel) + '" data-i="' + i + '">'
        + '<span class="wx-t">' + esc(hr(p.startTime)) + '</span><span class="wx-sym" aria-hidden="true">' + sym(p) + '</span>'
        + '<span class="wx-deg">' + esc(p.temperature) + '°</span>'
        + '<span class="wx-bar" aria-hidden="true"><i style="height:' + Math.max(r, 4) + '%"></i></span><span class="wx-pop">' + r + '%</span></button>';
    }).join('') + '</div>';
    var p = hrs[sel];
    var detail = '<p class="wx-detail"><strong>' + esc(hr(p.startTime)) + '</strong> ' + esc(p.shortForecast) + ', ' + esc(p.temperature) + '°' + esc(u)
      + ', ' + pop(p) + '% chance of rain, wind ' + esc(p.windDirection) + ' ' + esc(p.windSpeed) + '</p>';
    var labels = hrs.map(function (x) { return hr(x.startTime); });
    var dup = labels.some(function (l, i) { return labels.indexOf(l) !== i; });
    var note = dup ? '<p class="wx-note">Clocks fall back at 2 AM, so 1 AM happens twice: one extra hour on the dance floor.</p>' : '';
    return stats + strip + detail + note;
  }

  function weekView() {
    if (!week || !week.length) return '<p class="wx-msg">7-day forecast unavailable right now.</p>';
    return '<ul class="wx-week">' + week.map(function (p) {
      var s = Date.parse(p.startTime), e = Date.parse(p.endTime), party = Math.min(e, END) - Math.max(s, START) >= 4 * 3600000;
      return '<li' + (party ? ' class="is-party"' : '') + '><span class="wx-name">' + esc(p.name) + (party ? ' <em>Party</em>' : '') + '</span>'
        + '<span class="wx-sym" aria-hidden="true">' + sym(p) + '</span><span class="wx-deg">' + esc(p.temperature) + '°</span>'
        + '<span class="wx-desc">' + esc(p.shortForecast) + (pop(p) ? ' · ' + pop(p) + '% rain' : '') + '</span></li>';
    }).join('') + '</ul>';
  }

  function render() {
    if (failed) { body.innerHTML = '<p class="wx-msg">The live forecast couldn’t load right now. Use the link below for the full NWS forecast.</p>'; return; }
    if (!hourly) return;
    body.innerHTML = view === 'night' ? nightView() : weekView();
    var strip = body.querySelector('.wx-strip');
    if (strip) {
      var cur = strip.querySelector('[aria-selected="true"]');
      if (cur && cur.offsetLeft > strip.clientWidth) strip.scrollLeft = cur.offsetLeft - strip.clientWidth / 2;
    }
  }

  body.addEventListener('click', function (ev) {
    var b = ev.target.closest && ev.target.closest('.wx-hour');
    if (!b) return;
    var left = body.querySelector('.wx-strip').scrollLeft;
    sel = +b.getAttribute('data-i'); render();
    var s = body.querySelector('.wx-strip'); if (s) s.scrollLeft = left;
  });
  Array.prototype.forEach.call(tabs, function (t) {
    t.addEventListener('click', function () {
      view = t.getAttribute('data-view');
      Array.prototype.forEach.call(tabs, function (x) { x.setAttribute('aria-selected', String(x === t)); });
      render();
    });
  });

  get('https://api.weather.gov/points/' + box.getAttribute('data-lat') + ',' + box.getAttribute('data-lon'))
    .then(function (pt) { return Promise.all([get(pt.properties.forecastHourly), get(pt.properties.forecast).catch(function () { return null; })]); })
    .then(function (r) {
      hourly = r[0].properties.periods || [];
      week = r[1] ? r[1].properties.periods : null;
      var t = r[0].properties.updateTime || r[0].properties.generatedAt;
      if (t && upd) upd.textContent = '· updated ' + new Date(t).toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit', timeZone: TZ });
      if (!hourly.some(function (p) { var s = Date.parse(p.startTime); return s >= START && s < END; }) && Date.now() < START) {
        view = 'week'; Array.prototype.forEach.call(tabs, function (x) { x.setAttribute('aria-selected', String(x.getAttribute('data-view') === 'week')); });
      }
      render();
    })
    .catch(function () { failed = true; render(); });
})();
