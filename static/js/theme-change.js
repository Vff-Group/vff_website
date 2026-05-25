/**
 * Light / dark theme for Laundry UI
 */
(function () {
  'use strict';

  var root = document.documentElement;
  var body = document.body;
  var toggle = document.getElementById('checkbox') || document.querySelector('.theme-switch-input');

  function applyTheme(theme) {
    var isDark = theme === 'dark';
    root.setAttribute('data-theme', theme);
    if (body) {
      body.classList.toggle('vw-theme-dark', isDark);
      body.classList.toggle('vw-theme-light', !isDark);
    }
    if (toggle) {
      toggle.checked = isDark;
    }
  }

  var stored = localStorage.getItem('theme');
  if (stored === 'dark' || stored === 'light') {
    applyTheme(stored);
  } else {
    applyTheme('light');
  }

  if (toggle) {
    toggle.addEventListener('change', function (e) {
      var theme = e.target.checked ? 'dark' : 'light';
      localStorage.setItem('theme', theme);
      applyTheme(theme);
    });
  }
})();
