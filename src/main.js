(function () {
  var root = document.documentElement;

  // The veil parts once, on first load. A tap skips it.
  var intro = document.querySelector('.veil-intro');
  if (intro) {
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var gone = function () { root.classList.add('veil-open', 'veil-gone'); };
    if (reduce) { gone(); }
    else {
      setTimeout(function () { root.classList.add('veil-open'); }, 350);
      setTimeout(function () { root.classList.add('veil-gone'); }, 2100);
      window.addEventListener('pointerdown', gone, { once: true });
    }
  }

  // Sticky ticket button: shows after the hero, hides at the tickets section.
  var sticky = document.querySelector('.sticky');
  var hero = document.querySelector('.hero .actions');
  var tickets = document.getElementById('tickets');
  if (sticky && hero && tickets && 'IntersectionObserver' in window) {
    var heroVisible = true, ticketsVisible = false;
    var update = function () { sticky.classList.toggle('show', !heroVisible && !ticketsVisible); };
    new IntersectionObserver(function (e) { heroVisible = e[0].isIntersecting; update(); }).observe(hero);
    new IntersectionObserver(function (e) { ticketsVisible = e[0].isIntersecting; update(); }, { threshold: 0.15 }).observe(tickets);
  }

  // Video loads only when tapped.
  var video = document.querySelector('.video button');
  if (video) {
    video.addEventListener('click', function () {
      var id = video.getAttribute('data-id');
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
      f.title = 'Halloween 2025 recap';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.allowFullscreen = true;
      video.replaceWith(f);
    });
  }
})();
