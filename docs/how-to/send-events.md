# Send events

## From a link or button

Add `data-google-tag-event` to any link or button to send that event when it's clicked. Add parameters as JSON in `data-google-tag-params`:

```html
<a href="/pricing/"
   data-google-tag-event="select_content"
   data-google-tag-params='{"content_type": "cta", "content_id": "pricing-hero"}'>
  See pricing
</a>
```

A click sends one event. An email or phone link with its own `data-google-tag-event` sends only that event, not `contact_link_click` as well.

## From a script

The tag defines `window.wagtailGoogleTag`. It's there on every page, and sends nothing when the tag isn't loaded, so scripts never need to check:

```js
window.wagtailGoogleTag.track("generate_lead", { method: "newsletter" });
```

## See them in reports

A parameter on one of your events shows in Google Analytics' reports only after you create a custom dimension for it: see item 4 of [Set up Google Analytics](set-up-google-analytics.md).

The attributes and the function are listed in the reference: [HTML attributes and events](../reference/html-attributes.md) and [Script API](../reference/script-api.md).
