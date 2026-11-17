/**
 * SS PDP — interacciones de la landing de producto premium.
 *
 * Todo está encapsulado por sección (data root .ss-pdp). No se declara nada global
 * y no se modifica ningún comportamiento nativo de Horizon: el ATC utiliza el
 * formulario de producto del tema (<product-form-component>), por lo que el carrito,
 * los descuentos, el drawer y el checkout siguen siendo 100% nativos.
 */
(function () {
  'use strict';

  var SELECTORS = {
    galleryMain: '[data-ss-gallery-main]',
    thumb: '[data-ss-thumb]',
    bundle: '[data-ss-bundle]',
    productForm: 'form[data-ss-product-form]',
    ctaLabel: '[data-ss-cta-label]',
    stickyTitle: '[data-ss-sticky-title]',
    stickyNow: '[data-ss-sticky-now]',
    stickyWas: '[data-ss-sticky-was]',
    stickyBar: '[data-ss-sticky]',
    stickyCta: '[data-ss-sticky-cta]',
    sentinel: '[data-ss-sticky-sentinel]',
    accItem: '[data-ss-acc]',
    accButton: '[data-ss-acc-btn]',
    accBody: '[data-ss-acc-body]',
    marquee: '[data-ss-marquee]',
    slider: '[data-ss-slider]',
    sliderAfter: '[data-ss-slider-after]',
    sliderHandle: '[data-ss-slider-handle]',
    miniTrack: '[data-ss-mini-track]',
    miniDot: '[data-ss-mini-dot]',
    reviewsMore: '[data-ss-reviews-more]',
    toast: '[data-ss-toast]',
    toastText: '[data-ss-toast-text]'
  };

  function initRoot(root) {
    var $ = function (selector, context) {
      return (context || root).querySelector(selector);
    };
    var $$ = function (selector, context) {
      return Array.prototype.slice.call((context || root).querySelectorAll(selector));
    };

    /* ---------------------------------------------------------- Galería */
    var galleryMain = $(SELECTORS.galleryMain);
    if (galleryMain) {
      $$(SELECTORS.thumb).forEach(function (thumb) {
        thumb.addEventListener('click', function () {
          var target = thumb.getAttribute('data-ss-thumb');
          if (!target) return;

          $$(SELECTORS.thumb).forEach(function (other) {
            other.classList.remove('ss-active');
            other.setAttribute('aria-selected', 'false');
          });
          thumb.classList.add('ss-active');
          thumb.setAttribute('aria-selected', 'true');

          var srcset = thumb.getAttribute('data-ss-srcset') || '';

          galleryMain.style.opacity = '0';
          window.setTimeout(function () {
            galleryMain.src = target;
            if (srcset) {
              galleryMain.srcset = srcset;
            } else {
              galleryMain.removeAttribute('srcset');
            }
            galleryMain.style.opacity = '1';
          }, 160);
        });
      });
    }

    /* ------------------------------------------- Selector de packs (nativo)
     * Cambia la cantidad real que se envía al carrito, sin tocar la lógica
     * del tema: el input oculto quantity vive dentro del formulario de producto.
     */
    var form = $(SELECTORS.productForm) || document.querySelector(SELECTORS.productForm);
    var bundles = $$(SELECTORS.bundle);
    var ctaLabel = $(SELECTORS.ctaLabel);
    var stickyTitle = $(SELECTORS.stickyTitle);
    var stickyNow = $(SELECTORS.stickyNow);
    var stickyWas = $(SELECTORS.stickyWas);

    function selectBundle(bundle) {
      bundles.forEach(function (other) {
        other.classList.remove('ss-active');
        other.setAttribute('aria-checked', 'false');
        other.setAttribute('tabindex', '-1');
      });
      bundle.classList.add('ss-active');
      bundle.setAttribute('aria-checked', 'true');
      bundle.setAttribute('tabindex', '0');

      var quantity = bundle.getAttribute('data-ss-qty');
      var quantityInput = form ? form.querySelector('input[name="quantity"]') : null;
      if (quantityInput && quantity) quantityInput.value = quantity;
      if (form) form.setAttribute('data-ss-qty', quantity || '1');

      if (ctaLabel) {
        var label = bundle.getAttribute('data-ss-cta');
        if (label) ctaLabel.textContent = label;
      }

      var stickyTitleValue = bundle.getAttribute('data-ss-title');
      if (stickyTitle && stickyTitleValue) stickyTitle.textContent = stickyTitleValue;

      if (stickyNow) stickyNow.textContent = bundle.getAttribute('data-ss-price') || '';
      if (stickyWas) {
        var compare = bundle.getAttribute('data-ss-compare') || '';
        stickyWas.textContent = compare;
        stickyWas.hidden = !compare;
      }
    }

    bundles.forEach(function (bundle) {
      bundle.addEventListener('click', function () {
        selectBundle(bundle);
      });
      bundle.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          selectBundle(bundle);
        }
      });
    });

    /* -------------------------------------------------------- Acordeones */
    $$(SELECTORS.accItem).forEach(function (item) {
      var button = $(SELECTORS.accButton, item);
      var body = $(SELECTORS.accBody, item);
      if (!button || !body) return;

      button.addEventListener('click', function () {
        var isOpen = item.classList.contains('ss-open');
        var container = item.parentElement;

        Array.prototype.slice.call(container.children).forEach(function (sibling) {
          if (sibling === item) return;
          sibling.classList.remove('ss-open');
          var siblingBody = $(SELECTORS.accBody, sibling);
          if (siblingBody) siblingBody.style.maxHeight = '0px';
          var siblingButton = $(SELECTORS.accButton, sibling);
          if (siblingButton) siblingButton.setAttribute('aria-expanded', 'false');
        });

        if (isOpen) {
          item.classList.remove('ss-open');
          body.style.maxHeight = '0px';
          button.setAttribute('aria-expanded', 'false');
        } else {
          item.classList.add('ss-open');
          body.style.maxHeight = body.scrollHeight + 'px';
          button.setAttribute('aria-expanded', 'true');
        }
      });
    });

    /* ---------------------------------------------------- Marquee infinito */
    var marquee = $(SELECTORS.marquee);
    if (marquee) marquee.innerHTML += marquee.innerHTML;

    /* ------------------------------------------------ Slider antes/después */
    var slider = $(SELECTORS.slider);
    var sliderAfter = $(SELECTORS.sliderAfter);
    var sliderHandle = $(SELECTORS.sliderHandle);

    if (slider && sliderAfter && sliderHandle) {
      var dragging = false;

      var setSlider = function (clientX) {
        var rect = slider.getBoundingClientRect();
        var percentage = ((clientX - rect.left) / rect.width) * 100;
        percentage = Math.max(4, Math.min(96, percentage));
        sliderAfter.style.clipPath = 'inset(0 0 0 ' + percentage + '%)';
        sliderHandle.style.left = percentage + '%';
      };

      slider.addEventListener('pointerdown', function (event) {
        dragging = true;
        if (slider.setPointerCapture) slider.setPointerCapture(event.pointerId);
        setSlider(event.clientX);
      });
      slider.addEventListener('pointermove', function (event) {
        if (dragging) setSlider(event.clientX);
      });
      ['pointerup', 'pointercancel', 'pointerleave'].forEach(function (name) {
        slider.addEventListener(name, function () {
          dragging = false;
        });
      });
      slider.addEventListener('keydown', function (event) {
        if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
        event.preventDefault();
        var current = parseFloat(sliderHandle.style.left) || 50;
        var next = Math.max(4, Math.min(96, current + (event.key === 'ArrowRight' ? 4 : -4)));
        sliderAfter.style.clipPath = 'inset(0 0 0 ' + next + '%)';
        sliderHandle.style.left = next + '%';
      });
    }

    /* ------------------------------------------------ Mini reseñas: puntos */
    var miniTrack = $(SELECTORS.miniTrack);
    var miniDots = $$(SELECTORS.miniDot);
    if (miniTrack && miniDots.length) {
      miniTrack.addEventListener(
        'scroll',
        function () {
          var step = miniTrack.scrollWidth / miniDots.length;
          if (!step) return;
          var index = Math.round(miniTrack.scrollLeft / step);
          miniDots.forEach(function (dot, position) {
            dot.classList.toggle('ss-on', position === index);
          });
        },
        { passive: true }
      );
    }

    /* ------------------------------------------------------------- Toast */
    var toast = $(SELECTORS.toast);
    var toastText = $(SELECTORS.toastText);
    var toastTimer = null;

    function showToast(message) {
      if (!toast || !toastText) return;
      toastText.textContent = message || '';
      toast.classList.add('ss-show');
      window.clearTimeout(toastTimer);
      toastTimer = window.setTimeout(function () {
        toast.classList.remove('ss-show');
      }, 2600);
    }

    /* --------------------------------------------------- Reseñas: ver más */
    var reviewsMore = $(SELECTORS.reviewsMore);
    if (reviewsMore) {
      reviewsMore.addEventListener('click', function () {
        var reviewsSection = reviewsMore.closest('.ss-reviews');
        if (reviewsSection) reviewsSection.classList.add('ss-show-all');
        reviewsMore.hidden = true;
        showToast(reviewsMore.getAttribute('data-ss-more-message') || '');
      });
    }

    /* ------------------------------------------- Sticky ATC + envío al carrito
     * El botón sticky reenvía el formulario nativo (mismo ATC, mismo drawer,
     * mismos descuentos automáticos que el botón principal).
     */
    var stickyBar = $(SELECTORS.stickyBar);
    var sentinel = $(SELECTORS.sentinel);
    var stickyCta = $(SELECTORS.stickyCta);

    if (stickyBar && sentinel && 'IntersectionObserver' in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            stickyBar.classList.toggle('ss-visible', !entry.isIntersecting);
          });
        },
        { rootMargin: '0px 0px -1px 0px', threshold: 0 }
      );
      observer.observe(sentinel);
    }

    if (stickyCta && form) {
      stickyCta.addEventListener('click', function () {
        var submitter = form.querySelector('[ref="addToCartButton"]');
        if (submitter && submitter.disabled) return;
        if (typeof form.requestSubmit === 'function') {
          submitter ? form.requestSubmit(submitter) : form.requestSubmit();
        } else {
          form.submit();
        }
      });
    }

    /* --------------------------------- Recálculo de alturas de acordeón abierto */
    window.addEventListener('resize', function () {
      $$(SELECTORS.accItem).forEach(function (item) {
        if (!item.classList.contains('ss-open')) return;
        var body = $(SELECTORS.accBody, item);
        if (body) body.style.maxHeight = body.scrollHeight + 'px';
      });
    });
  }

  function init() {
    document.querySelectorAll('.ss-pdp').forEach(initRoot);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* Reliable add-to-cart for the custom pack selector. Runs before Horizon's
   delegated submit listener; Shopify applies the existing BxGy discounts. */
(function () {
  'use strict';
  function onReady() {
    document.querySelectorAll('.ss-pdp form[data-ss-product-form]').forEach(function (form) {
      if (form.dataset.ssCartBound) return;
      form.dataset.ssCartBound = 'true';
      form.addEventListener('submit', async function (event) {
        event.preventDefault();
        event.stopImmediatePropagation();
        var button = form.querySelector('[data-ss-main-cta]');
        var variant = form.querySelector('input[name="id"]');
        var quantity = form.querySelector('input[name="quantity"]');
        if (!variant || !variant.value) {
          window.alert('No se pudo identificar el producto. Actualiza la página.');
          return;
        }
        var count = Math.max(1, Number(quantity && quantity.value) || 1);
        if (button) { button.disabled = true; button.setAttribute('aria-busy', 'true'); }
        try {
          var response = await fetch((window.Shopify && Shopify.routes && Shopify.routes.root || '/') + 'cart/add.js', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify({ items: [{ id: Number(variant.value), quantity: count }] })
          });
          var result = await response.json();
          if (!response.ok) throw new Error(result.description || result.message || 'No se pudo añadir el producto');
          window.location.assign((window.Shopify && Shopify.routes && Shopify.routes.root || '/') + 'cart');
        } catch (error) {
          if (button) { button.disabled = false; button.removeAttribute('aria-busy'); }
          window.alert(error.message || 'Error al añadir al carrito. Inténtalo de nuevo.');
        }
      }, true);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', onReady);
  else onReady();
})();
