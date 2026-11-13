/**
 * Wagtail Google tag: loads Google's tag with Consent Mode defaults, and
 * defines window.wagtailGoogleTag:
 *
 * - track(name, params) sends an event.
 * - consent({ analytics, marketing }) updates Consent Mode with a visitor's
 *   choice. A "wagtail-cookie-consent:change" event on document, with the same
 *   object as its detail, does the same. When analytics is refused, Google
 *   Analytics' cookies are deleted too, and the User-ID is cleared.
 * - user(id) sets Google Analytics' User-ID for the events that follow, and
 *   user(null) clears it.
 *
 * All three do nothing when the tag isn't loaded (no measurement ID, a preview, or
 * a visitor the site leaves out of tracking), so pages never need to check.
 *
 * Clicks on elements with data-google-tag-event send that event, with
 * parameters from data-google-tag-params (JSON). Clicks on email and phone
 * links send contact_link_click, unless the link has its own event.
 *
 * Google's tag is installed the way Google documents it now: its script from
 * gtm.js and no "config" command, which is deprecated. Google's tag sends the
 * page view itself, and parameters go on events only.
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

    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtm.js?id=${encodeURIComponent(config.id)}`;
    document.head.appendChild(script);
  }

  const track = (name, params) => {
    if (enabled && name) gtag('event', name, params || {});
  };

  /**
   * Deletes Google Analytics' cookies (_ga and _ga_<ID>). Google's tag stops
   * using them when analytics is denied, but leaves them in place. A cookie
   * can only be deleted with the domain it was set on, which Google picks, so
   * each domain this page could have set one on is tried.
   */
  const deleteAnalyticsCookies = () => {
    const names = document.cookie
      .split(';')
      .map((cookie) => cookie.split('=')[0].trim())
      .filter((name) => name === '_ga' || name.startsWith('_ga_'));
    if (!names.length) return;
    const labels = window.location.hostname.split('.');
    const domains = [''];
    for (let i = 0; i < labels.length; i += 1) {
      domains.push(`; domain=${labels.slice(i).join('.')}`);
    }
    names.forEach((name) => {
      domains.forEach((domain) => {
        document.cookie = `${name}=; path=/; max-age=0${domain}`;
      });
    });
  };

  /**
   * Sets Google Analytics' User-ID, or clears it with null. Google's rule for
   * signing out is null, never an empty string.
   */
  const user = (id) => {
    if (enabled) gtag('set', { user_id: id ? String(id) : null });
  };

  const consent = (choice) => {
    if (!enabled || !choice) return;
    const update = {};
    if ('analytics' in choice) {
      update.analytics_storage = choice.analytics ? 'granted' : 'denied';
      if (!choice.analytics) {
        deleteAnalyticsCookies();
        user(null);
      }
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

  window.wagtailGoogleTag = { track, consent, user };

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
