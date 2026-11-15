# Connect a consent banner

Google's tag starts with the defaults described in [Consent](../explanation/consent.md). A consent banner updates these defaults with the visitor's choice, in either of two ways:

```js
// Call the function
window.wagtailGoogleTag.consent({ analytics: true, marketing: false });

// Or send this event on document
document.dispatchEvent(
  new CustomEvent("wagtail-cookie-consent:change", {
    detail: { analytics: true, marketing: false },
  }),
);
```

`analytics` sets analytics storage. `marketing` sets the advertising signals, and only when **Site uses Google Ads** is on. A banner that runs on each page load once a visitor has chosen should send the choice each time, as early as it can: Google's tag waits half a second for that update before it sends anything, and a choice that arrives later misses the page view.

The event comes from [wagtail-cookie-consent](https://github.com/Limitless-Horizons/wagtail-cookie-consent), a companion package, but any banner can send it or call the function. With that package, put `{% google_tag %}` before `{% cookie_consent %}`.

In Google Analytics, check the two consent settings in item 5 of [Set up Google Analytics](set-up-google-analytics.md).
