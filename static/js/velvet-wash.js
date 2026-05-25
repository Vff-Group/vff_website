/**
 * Velvet Wash — site interactions
 */
(function () {
  'use strict';

  /* Scroll reveal */
  var revealEls = document.querySelectorAll('.vw-reveal');
  if (revealEls.length && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    revealEls.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    revealEls.forEach(function (el) {
      el.classList.add('visible');
    });
  }

  /* Header scroll state */
  var header = document.getElementById('site-header');
  if (header) {
    var onScroll = function () {
      if (window.scrollY > 60) {
        header.classList.add('nav-fixed');
      } else {
        header.classList.remove('nav-fixed');
      }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }
})();
