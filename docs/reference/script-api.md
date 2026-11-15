# Script API

The tag defines `window.wagtailGoogleTag` on every page. Its functions send nothing when Google's tag isn't loaded (no measurement ID, a preview, or a visitor the site leaves out of tracking), so scripts never need to check.

## `track(name, params)`

Sends an event.

```js
window.wagtailGoogleTag.track("generate_lead", { method: "newsletter" });
```

- `name`: the event's name. Nothing is sent without one.
- `params`: an object of event parameters. Optional.

## `consent(choice)`

Updates Consent Mode with a visitor's choice.

```js
window.wagtailGoogleTag.consent({ analytics: true, marketing: false });
```

- `analytics`: `true` grants analytics storage, `false` denies it. On `false`, the package also deletes Google Analytics' cookies (`_ga` and those starting with `_ga_`) and clears the User-ID.
- `marketing`: sets the advertising signals (`ad_storage`, `ad_user_data`, `ad_personalization`), and only when **Site uses Google Ads** is on.

A key that's left out isn't changed.

## `user(id)`

Sets Google Analytics' User-ID for the events that follow. `user(null)` clears it.

```js
window.wagtailGoogleTag.user("3f6c1a52-9d0e-4c7b-8a41-5e2b7d90c1aa");
window.wagtailGoogleTag.user(null);
```

See [Set a User-ID](../how-to/set-a-user-id.md) for Google's rules.

## The `wagtail-cookie-consent:change` event

An event of this name on `document`, with the same object as its `detail`, does what `consent(choice)` does:

```js
document.dispatchEvent(
  new CustomEvent("wagtail-cookie-consent:change", {
    detail: { analytics: true, marketing: false },
  }),
);
```

[wagtail-cookie-consent](https://github.com/Limitless-Horizons/wagtail-cookie-consent) sends it; any banner can.
