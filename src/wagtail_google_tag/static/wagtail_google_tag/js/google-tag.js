/**
 * Wagtail Google tag: loads Google's tag with Consent Mode defaults, and
 * defines window.wagtailGoogleTag:
 *
 * - track(name, params) sends an event.
 * - consent({ analytics, marketing }) updates Consent Mode with a visitor's
 *   choice. A "wagtail-cookie-consent:change" event on document, with the same
 *   object as its detail, does the same.
 *
 * Both do nothing when the tag isn't loaded (no measurement ID, a preview, or
 * a signed-in user who isn't tracked), so pages never need to check.
 *
 * Clicks on elements with data-google-tag-event send that event, with
 * parameters from data-google-tag-params (JSON). Clicks on email and phone
 * links send contact_link_click, unless the link has its own event.
 */
(() => {
  if (window.wagtailGoogleTag) return;

  const configElement = document.getElementById('wagtail-google-tag-config');
  const config = configElement ? JSON.parse(configElement.textContent) : {};
  const enabled = Boolean(config.id);

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    // Google's tag reads the arguments object itself, not an array.
    window.dataLayer.push(arguments);
  }

  if (enabled) {
    window.gtag = gtag;
    config.consent.forEach((defaults) => gtag('consent', 'default', defaults));
    gtag('js', new Date());
    gtag('config', config.id, config.params);

    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(config.id)}`;
    document.head.appendChild(script);
  }

  const track = (name, params) => {
    if (enabled && name) gtag('event', name, params || {});
  };

  const consent = (choice) => {
    if (!enabled || !choice) return;
    const update = {};
    if ('analytics' in choice) {
      update.analytics_storage = choice.analytics ? 'granted' : 'denied';
    }
    // Ad signals stay denied unless the site uses Google Ads.
    if (config.ads && 'marketing' in choice) {
      const value = choice.marketing ? 'granted' : 'denied';
      update.ad_storage = value;
      update.ad_user_data = value;
      update.ad_personalization = value;
    }
    if (Object.keys(update).length) gtag('consent', 'update', update);
  };

  window.wagtailGoogleTag = { track, consent };

  document.addEventListener('wagtail-cookie-consent:change', (event) => {
    consent(event.detail);
  });

  const parseParams = (element) => {
    const json = element.getAttribute('data-google-tag-params');
    if (!json) return {};
    try {
      return JSON.parse(json);
    } catch {
      return {};
    }
  };

  document.addEventListener('click', (event) => {
    if (!enabled || !(event.target instanceof Element)) return;

    const tagged = event.target.closest('[data-google-tag-event]');
    if (tagged) {
      track(tagged.getAttribute('data-google-tag-event'), parseParams(tagged));
      return;
    }

    if (!config.contactLinks) return;
    const link = event.target.closest('a[href]');
    if (!link) return;
    // No address or number is sent: GA forbids personal data.
    if (link.protocol === 'mailto:') {
      track('contact_link_click', { link_type: 'email' });
    } else if (link.protocol === 'tel:') {
      track('contact_link_click', { link_type: 'phone' });
    }
  });
})();
