import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import { JSDOM } from 'jsdom';

const SCRIPT = readFileSync(
  new URL(
    '../../src/wagtail_google_tag/static/wagtail_google_tag/js/google-tag.js',
    import.meta.url,
  ),
  'utf8',
);

const ENABLED = {
  id: 'G-TEST123',
  consent: [
    {
      analytics_storage: 'granted',
      ad_storage: 'denied',
      wait_for_update: 500,
    },
    { analytics_storage: 'denied', region: ['DE'], wait_for_update: 500 },
  ],
  ads: false,
  contactLinks: true,
};

/** A page with the tag's config and the given body, with the script run. */
function page(config, body = '') {
  const json = JSON.stringify(config);
  const dom = new JSDOM(
    `<!doctype html><html><head><script id="wagtail-google-tag-config" type="application/json">${json}</script></head><body>${body}</body></html>`,
    { runScripts: 'outside-only', url: 'https://example.com/' },
  );
  dom.window.eval(SCRIPT);
  return dom.window;
}

/** dataLayer entries as plain arrays, copied out of the page's realm. */
const calls = (window) =>
  JSON.parse(
    JSON.stringify(window.dataLayer.map((entry) => Array.from(entry))),
  );
const events = (window) =>
  calls(window)
    .filter(([command]) => command === 'event')
    .map(([, name, params]) => [name, params]);

const click = (window, selector) =>
  window.document
    .querySelector(selector)
    .dispatchEvent(
      new window.MouseEvent('click', { bubbles: true, cancelable: true }),
    );

test("consent defaults come first, and Google's tag loads without config", () => {
  const window = page(ENABLED);
  const commands = calls(window).map(([command, kind]) =>
    command === 'consent' ? `consent ${kind}` : command,
  );
  // No "config" command: Google has deprecated it.
  assert.deepEqual(commands, ['consent default', 'consent default', 'js']);
  const script = window.document.querySelector(
    'script[src^="https://www.googletagmanager.com/"]',
  );
  assert.equal(
    script.src,
    'https://www.googletagmanager.com/gtm.js?id=G-TEST123',
  );
  assert.equal(script.async, true);
});

test('without an ID, nothing loads and the API sends nothing', () => {
  const window = page({ id: null }, '<a href="mailto:a@example.com">Mail</a>');
  window.wagtailGoogleTag.track('share', { method: 'email' });
  window.wagtailGoogleTag.consent({ analytics: true });
  click(window, 'a');
  assert.deepEqual(calls(window), []);
  assert.equal(window.gtag, undefined);
  assert.equal(window.document.querySelectorAll('script[src]').length, 0);
});

test('without the config element, the API still exists', () => {
  const dom = new JSDOM('<!doctype html><html><body></body></html>', {
    runScripts: 'outside-only',
  });
  dom.window.eval(SCRIPT);
  assert.equal(typeof dom.window.wagtailGoogleTag.track, 'function');
  dom.window.wagtailGoogleTag.track('share');
  assert.deepEqual(calls(dom.window), []);
});

test('the script runs once if included twice', () => {
  const window = page(ENABLED);
  const count = window.dataLayer.length;
  window.eval(SCRIPT);
  assert.equal(window.dataLayer.length, count);
});

test('track() sends an event', () => {
  const window = page(ENABLED);
  window.wagtailGoogleTag.track('generate_lead', { method: 'contact_form' });
  assert.deepEqual(events(window), [
    ['generate_lead', { method: 'contact_form' }],
  ]);
});

test('track() without params sends an empty object', () => {
  const window = page(ENABLED);
  window.wagtailGoogleTag.track('sign_up');
  assert.deepEqual(events(window), [['sign_up', {}]]);
});

test('data-google-tag-event sends its event with its params', () => {
  const window = page(
    ENABLED,
    `<button data-google-tag-event="share" data-google-tag-params='{"method": "copy_link", "item_id": "slug"}'><span>Copy</span></button>`,
  );
  click(window, 'span');
  assert.deepEqual(events(window), [
    ['share', { method: 'copy_link', item_id: 'slug' }],
  ]);
});

test('bad params JSON still sends the event', () => {
  const window = page(
    ENABLED,
    `<button data-google-tag-event="select_content" data-google-tag-params="{oops">Go</button>`,
  );
  click(window, 'button');
  assert.deepEqual(events(window), [['select_content', {}]]);
});

test('email and phone links send contact_link_click without the address', () => {
  const window = page(
    ENABLED,
    '<a id="m" href="MAILTO:someone@example.com">Mail</a><a id="t" href="tel:+15551234567">Call</a><a id="w" href="/about/">About</a>',
  );
  click(window, '#m');
  click(window, '#t');
  click(window, '#w');
  assert.deepEqual(events(window), [
    ['contact_link_click', { link_type: 'email' }],
    ['contact_link_click', { link_type: 'phone' }],
  ]);
  assert.doesNotMatch(JSON.stringify(calls(window)), /someone|5551234567/);
});

test('a mailto link with its own event sends only that event', () => {
  const window = page(
    ENABLED,
    `<a href="mailto:?subject=Hi" data-google-tag-event="share" data-google-tag-params='{"method": "email"}'>Share by email</a>`,
  );
  click(window, 'a');
  assert.deepEqual(events(window), [['share', { method: 'email' }]]);
});

test("contact links aren't tracked when turned off", () => {
  const window = page(
    { ...ENABLED, contactLinks: false },
    '<a href="mailto:someone@example.com">Mail</a>',
  );
  click(window, 'a');
  assert.deepEqual(events(window), []);
});

const updates = (window) =>
  calls(window)
    .filter(([command, kind]) => command === 'consent' && kind === 'update')
    .map(([, , update]) => update);

test('consent() updates analytics, and ad signals stay denied without ads', () => {
  const window = page(ENABLED);
  window.wagtailGoogleTag.consent({ analytics: true, marketing: true });
  window.wagtailGoogleTag.consent({ analytics: false });
  assert.deepEqual(updates(window), [
    { analytics_storage: 'granted' },
    { analytics_storage: 'denied' },
  ]);
});

test('consent() updates ad signals when the site uses ads', () => {
  const window = page({ ...ENABLED, ads: true });
  window.wagtailGoogleTag.consent({ analytics: false, marketing: true });
  assert.deepEqual(updates(window), [
    {
      analytics_storage: 'denied',
      ad_storage: 'granted',
      ad_user_data: 'granted',
      ad_personalization: 'granted',
    },
  ]);
});

const cookieNames = (window) =>
  window.document.cookie
    .split(';')
    .map((cookie) => cookie.split('=')[0].trim())
    .filter(Boolean)
    .sort();

test("refusing analytics deletes Google Analytics' cookies, and only those", () => {
  const window = page(ENABLED);
  window.document.cookie = '_ga=GA1.1.1.1; path=/; domain=example.com';
  window.document.cookie = '_ga_TEST123=GS1.1.1; path=/; domain=example.com';
  window.document.cookie = '_gallery=1; path=/';
  window.document.cookie = 'csrftoken=abc; path=/';
  window.wagtailGoogleTag.consent({ analytics: true });
  assert.deepEqual(cookieNames(window), [
    '_ga',
    '_ga_TEST123',
    '_gallery',
    'csrftoken',
  ]);
  window.wagtailGoogleTag.consent({ analytics: false });
  assert.deepEqual(cookieNames(window), ['_gallery', 'csrftoken']);
});

test("cookies set on the page's own host are deleted too", () => {
  const window = page(ENABLED);
  window.document.cookie = '_ga=GA1.1.1.1; path=/';
  window.wagtailGoogleTag.consent({ analytics: false });
  assert.deepEqual(cookieNames(window), []);
});

test('without the tag, no cookie is touched', () => {
  const window = page({ id: null });
  window.document.cookie = '_ga=GA1.1.1.1; path=/';
  window.wagtailGoogleTag.consent({ analytics: false });
  assert.deepEqual(cookieNames(window), ['_ga']);
});

test('the wagtail-cookie-consent:change event updates consent', () => {
  const window = page(ENABLED);
  window.document.dispatchEvent(
    new window.CustomEvent('wagtail-cookie-consent:change', {
      detail: { analytics: true, marketing: false },
    }),
  );
  assert.deepEqual(updates(window), [{ analytics_storage: 'granted' }]);
});

test('a change event without a choice is ignored', () => {
  const window = page(ENABLED);
  window.document.dispatchEvent(
    new window.CustomEvent('wagtail-cookie-consent:change'),
  );
  assert.deepEqual(updates(window), []);
});

const userIds = (window) =>
  calls(window)
    .filter(([command]) => command === 'set')
    .map(([, values]) => values.user_id);

test('user() sets the User-ID, and user(null) clears it', () => {
  const window = page(ENABLED);
  window.wagtailGoogleTag.user('lead-123');
  window.wagtailGoogleTag.user(42);
  window.wagtailGoogleTag.user(null);
  window.wagtailGoogleTag.user('');
  // Google's rule for "no user" is null, never an empty string.
  assert.deepEqual(userIds(window), ['lead-123', '42', null, null]);
});

test('refusing analytics clears the User-ID, and allowing it leaves it alone', () => {
  const window = page(ENABLED);
  window.wagtailGoogleTag.user('lead-123');
  window.wagtailGoogleTag.consent({ analytics: true });
  assert.deepEqual(userIds(window), ['lead-123']);
  window.wagtailGoogleTag.consent({ analytics: false });
  assert.deepEqual(userIds(window), ['lead-123', null]);
});

test('without the tag, user() sends nothing', () => {
  const window = page({ id: null });
  window.wagtailGoogleTag.user('lead-123');
  assert.deepEqual(calls(window), []);
});
