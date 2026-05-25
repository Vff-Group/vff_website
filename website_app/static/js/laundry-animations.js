/**
 * Velvet Wash — scroll reveals, header, counters, video lazy-load
 */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Header on scroll */
  var header = document.querySelector('.lw-header');
  if (header) {
    var onHeaderScroll = function () {
      header.classList.toggle('lw-header--scrolled', window.scrollY > 24);
    };
    window.addEventListener('scroll', onHeaderScroll, { passive: true });
    onHeaderScroll();
  }

  /* Stagger children */
  document.querySelectorAll('.lw-stagger').forEach(function (group) {
    Array.from(group.children).forEach(function (el, i) {
      el.classList.add('lw-stagger-item', 'lw-reveal');
      el.style.setProperty('--lw-stagger-i', i);
    });
  });

  /* Scroll reveal */
  function initReveal(selector, visibleClass) {
    var els = document.querySelectorAll(selector);
    if (!els.length) return;
    if (reduced || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add(visibleClass); });
      return;
    }
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add(visibleClass);
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08, rootMargin: '0px 0px -32px 0px' }
    );
    els.forEach(function (el) { io.observe(el); });
  }

  initReveal('.lw-reveal', 'lw-reveal--visible');
  initReveal('.lw-reveal-left', 'lw-reveal--visible');
  initReveal('.lw-reveal-right', 'lw-reveal--visible');
  initReveal('.lw-reveal-scale', 'lw-reveal--visible');

  /* Stats counter */
  var statNums = document.querySelectorAll('.lw-stats-bar__item strong[data-count]');
  if (statNums.length && !reduced) {
    var countIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var end = parseInt(el.getAttribute('data-count'), 10);
        var suffix = el.getAttribute('data-suffix') || '';
        var start = 0;
        var dur = 1400;
        var t0 = performance.now();
        function tick(now) {
          var p = Math.min((now - t0) / dur, 1);
          var ease = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.floor(start + (end - start) * ease) + suffix;
          if (p < 1) requestAnimationFrame(tick);
          else countIo.unobserve(el);
        }
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.5 });
    statNums.forEach(function (el) { countIo.observe(el); });
  }

  /* Video showcase lazy load */
  var videos = document.querySelectorAll('.lw-video-showcase video[data-src]');
  if (videos.length && 'IntersectionObserver' in window) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var v = entry.target;
        if (entry.isIntersecting) {
          if (!v.src && v.dataset.src) {
            v.src = v.dataset.src;
            v.play().catch(function () {});
          }
        } else if (v.src) {
          v.pause();
        }
      });
    }, { rootMargin: '80px', threshold: 0.2 });
    videos.forEach(function (v) { vio.observe(v); });
  } else if (videos.length) {
    videos.forEach(function (v) {
      if (v.dataset.src) { v.src = v.dataset.src; v.play().catch(function () {}); }
    });
  }

  /* Back to top */
  var movetop = document.getElementById('movetop');
  if (movetop) {
    window.addEventListener('scroll', function () {
      movetop.classList.toggle('lw-movetop--visible', window.scrollY > 280);
    }, { passive: true });
  }
})();
