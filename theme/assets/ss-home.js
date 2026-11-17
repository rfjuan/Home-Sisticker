/**
 * SS Home — interacciones de la homepage.
 *
 * Solo gestiona el CTA fijo de móvil. El resto de interacciones (comparador,
 * acordeones de la FAQ) las resuelve ss-pdp.js, que también se carga en el index.
 */
(function () {
  'use strict';

  var bar = null;
  var link = null;
  var ticking = false;
  var isVisible = false;

  function setVisible(next) {
    if (!bar || next === isVisible) return;
    isVisible = next;
    bar.classList.toggle('is-visible', next);
    bar.setAttribute('aria-hidden', next ? 'false' : 'true');
    if (link) link.tabIndex = next ? 0 : -1;
  }

  function update() {
    ticking = false;
    if (!bar) return;

    if (window.matchMedia('(min-width: 750px)').matches) {
      setVisible(false);
      return;
    }

    var scrollTop = window.pageYOffset || document.documentElement.scrollTop || 0;
    var viewport = window.innerHeight || 0;

    var footer = document.querySelector('footer');
    var footerTop = footer
      ? footer.getBoundingClientRect().top + scrollTop
      : document.documentElement.scrollHeight;

    var pastHero = scrollTop > Math.min(520, viewport * 0.75);
    var beforeFooter = scrollTop + viewport < footerTop + 120;

    setVisible(pastHero && beforeFooter);
  }

  function onScroll() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(update);
  }

  function init() {
    bar = document.querySelector('[data-ss-home-sticky]');
    link = bar ? bar.querySelector('a') : null;
    isVisible = false;
    if (bar) bar.classList.remove('is-visible');
    update();
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  window.addEventListener('load', update);

  // Compatibilidad con el editor de Shopify: al cargar o recargar una sección.
  document.addEventListener('shopify:section:load', init);
  document.addEventListener('shopify:section:select', update);

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
