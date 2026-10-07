(function () {
  var data = window.__VEIL__;
  var form = document.getElementById('gate-form');
  var input = document.getElementById('code');
  var error = document.getElementById('gate-error');
  var gate = document.getElementById('gate');
  var guide = document.getElementById('guide');
  var body = document.getElementById('guide-body');
  var KEY = 'btv-gate';

  function b64(s) { return Uint8Array.from(atob(s), function (c) { return c.charCodeAt(0); }); }
  function normalize(v) { return v.toUpperCase().replace(/[^A-Z0-9]/g, ''); }

  function open(code) {
    var enc = new TextEncoder();
    return crypto.subtle.importKey('raw', enc.encode(normalize(code)), 'PBKDF2', false, ['deriveKey'])
      .then(function (base) {
        return crypto.subtle.deriveKey(
          { name: 'PBKDF2', salt: b64(data.salt), iterations: data.iter, hash: 'SHA-256' },
          base, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
      })
      .then(function (key) { return crypto.subtle.decrypt({ name: 'AES-GCM', iv: b64(data.iv) }, key, b64(data.ct)); })
      .then(function (plain) {
        body.innerHTML = new TextDecoder().decode(plain);
        gate.hidden = true;
        guide.hidden = false;
        try { localStorage.setItem(KEY, code); } catch (e) {}
        window.scrollTo(0, 0);
        return true;
      });
  }

  // Returning guests on the same phone open straight to the guide.
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (saved) { open(saved).catch(function () { try { localStorage.removeItem(KEY); } catch (e) {} }); }

  form.addEventListener('submit', function (ev) {
    ev.preventDefault();
    error.hidden = true;
    var btn = form.querySelector('button');
    btn.disabled = true;
    open(input.value)
      .catch(function () { error.hidden = false; input.select(); })
      .then(function () { btn.disabled = false; });
  });
})();
