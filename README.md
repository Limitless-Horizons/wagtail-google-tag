# Wagtail Google tag

Google tag (GA4) for Wagtail. Goal is everything you need to do to set up GA, you do through the Wagtail admin: per-site settings, Consent Mode defaults, page data and click events.

Claude Code was used with oversight by the maintainer.

## What it is

Wagtail Google tag adds Google's tag for Google Analytics 4 to a Wagtail site. Each site's measurement ID and options are set in the Wagtail admin. The tag loads with Consent Mode defaults that keep visitors in Europe out of analytics cookies until they agree, and it stays out of previews and away from signed-in editors. Pages can add their own data to each page view, and links and buttons can send events with two HTML attributes.

It doesn't bring Google Analytics into the Wagtail admin: reports, key events and data retention stay in Google Analytics. It also doesn't load Google Tag Manager containers or send server-side events.

## Requirements

- Wagtail 7.4, 8.0 or 8.1, with the [Python and Django versions](https://docs.wagtail.org/en/stable/releases/upgrading.html#compatible-django-python-versions) each of them supports
- `wagtail.contrib.settings`, which comes with Wagtail

## Installation

1. Install the package:

   ```sh
   pip install wagtail-google-tag
   ```

2. Add it to `INSTALLED_APPS`, with `wagtail.contrib.settings`:

   ```python
   INSTALLED_APPS = [
       # ...
       "wagtail.contrib.settings",
       "wagtail_google_tag",
       # ...
   ]
   ```

3. Create its table:

   ```sh
   python manage.py migrate
   ```

4. Add the tag near the top of `<head>` in your base template:

   ```django
   {% load wagtail_google_tag %}
   <!doctype html>
   <html>
     <head>
       <meta charset="utf-8">
       {% google_tag %}
       ...
   ```

5. In the Wagtail admin, go to **Settings → Google tag** and enter your GA4 measurement ID. In Google Analytics, it's under **Admin → Data streams**.

## What you get out of the box

- A `page_view` for every page, with GA's built-in `content_group` set to the page type, such as "Blog page".
- Google Analytics' own automatic tracking (enhanced measurement), such as scrolls, outbound clicks and site search, as you set it up in Google Analytics.
- [Consent Mode](#consent) defaults: analytics denied in Europe until a visitor agrees, and Google's advertising signals denied everywhere unless your site uses Google Ads.
- A `contact_link_click` event when a visitor clicks an email or phone link. Google Analytics' automatic tracking doesn't cover these.
- Nothing sent from Wagtail previews, or for signed-in users such as editors.

## Usage

### Click events

Add `data-google-tag-event` to any link or button to send that event when it's clicked. Add parameters as JSON in `data-google-tag-params`:

```html
<a href="/pricing/"
   data-google-tag-event="select_content"
   data-google-tag-params='{"content_type": "cta", "content_id": "pricing-hero"}'>
  See pricing
</a>
```

A click sends one event. An email or phone link with its own `data-google-tag-event` sends only that event, not `contact_link_click` as well.

### Page data

A page model can supply the parameters for its page view with `get_google_tag_params()`. Start from the defaults to keep the content group:

```python
from wagtail.models import Page
from wagtail_google_tag.tag import default_page_params


class BlogPage(Page):
    ...

    def get_google_tag_params(self):
        params = default_page_params(self)  # {"content_group": "Blog page"}
        params["blog_category"] = self.category.name
        return params
```

To see a parameter like `blog_category` in Google Analytics' reports, register it there as a custom dimension.

### From scripts

The tag defines `window.wagtailGoogleTag`. It's there on every page, and sends nothing when the tag isn't loaded, so scripts never need to check:

```js
window.wagtailGoogleTag.track("generate_lead", { method: "newsletter" });
```

### Templates without a Wagtail page

Pages that aren't Wagtail pages, such as a 404 page, can pass their own parameters:

```django
{% google_tag content_group="Not found" %}
```

These are added to the page's own parameters, and win if both set the same one.

## Consent

Before a visitor has made a choice, Google's tag starts with these Consent Mode defaults:

| Visitors | Analytics | Advertising signals |
|---|---|---|
| In the European Economic Area, the UK and Switzerland | Denied | Denied |
| Everywhere else | Granted | Denied, unless "Site uses Google Ads" is on |

Google works out where a visitor is. Denied analytics means no analytics cookies: Google Analytics receives only cookieless pings. To start with analytics granted everywhere, turn off **Deny analytics by default in Europe**.

A consent banner updates these defaults with the visitor's choice, in either of two ways:

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

`analytics` sets analytics storage. `marketing` sets the advertising signals, and only when **Site uses Google Ads** is on. A banner that runs on each page load once a visitor has chosen should send the choice each time. In Europe, Google's tag waits half a second for that update before it sends anything.

The event comes from [wagtail-cookie-consent](https://github.com/Limitless-Horizons/wagtail-cookie-consent), a companion package in development, but any banner can send it or call the function.

## Settings reference

Each site has its own settings, under **Settings → Google tag**.

| Setting | Default | What it does |
|---|---|---|
| Measurement ID | Blank | The site's GA4 measurement ID (`G-…`). Blank means no tag, unless the Django setting below supplies one. |
| Deny analytics by default in Europe | On | The Europe defaults in [Consent](#consent). |
| Site uses Google Ads | Off | When off, advertising signals are denied for every visitor. |
| Track signed-in users | Off | When off, visits by signed-in users aren't tracked. |
| Track email and phone links | On | Sends `contact_link_click` with `link_type` set to `email` or `phone`. |
| Debug mode | Off | Sends events to Google Analytics' DebugView, for testing. |

`WAGTAIL_GOOGLE_TAG_MEASUREMENT_ID` in your Django settings is a fallback, used by any site whose measurement ID is blank. It's useful for moving an existing tag over, or for setting the ID from an environment variable.

### Testing your setup

Turn on **Debug mode**, then visit your site in a private window, since your own signed-in visits aren't tracked. Your page views and events show up in Google Analytics under **Admin → DebugView**. Turn debug mode off when you're done.

### Content Security Policy

If your site has a Content Security Policy, allow Google's tag: `https://www.googletagmanager.com` in `script-src`, and Google Analytics' collection domains, such as `https://*.google-analytics.com`, in `connect-src`. The package itself uses no inline scripts.

## Privacy notes

The package sends no personal data. Email and phone link events carry only `link_type`, never the address or number. Google's own rules forbid personal data in Google Analytics, so keep it out of your own event parameters too.

Some things are set in Google Analytics, not here:

- How long data is kept (Google's default is two months)
- Which events count as key events, such as `generate_lead`
- Custom dimensions for your own parameters
- Enhanced measurement: scrolls, outbound clicks, site search and the rest

## Links

- [Changelog](https://github.com/Limitless-Horizons/wagtail-google-tag/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/Limitless-Horizons/wagtail-google-tag/blob/main/CONTRIBUTING.md)
- [Security policy](https://github.com/Limitless-Horizons/wagtail-google-tag/blob/main/SECURITY.md)

## License

BSD-3-Clause. See [LICENSE](https://github.com/Limitless-Horizons/wagtail-google-tag/blob/main/LICENSE).
