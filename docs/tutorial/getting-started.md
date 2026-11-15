# Getting started

From installing the package to seeing your own visit in Google Analytics. You need a Wagtail site and a Google Analytics 4 property with a web data stream.

## Requirements

- Wagtail 7.4, 8.0 or 8.1, with the [Python and Django versions](https://docs.wagtail.org/en/stable/releases/upgrading.html#compatible-django-python-versions) each of them supports
- `wagtail.contrib.settings`, which comes with Wagtail
- `django.template.context_processors.request` in your template settings. Wagtail's project template has it. Without it, the tag loads nothing.

## Install the package and add the tag

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

3. Create its tables:

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

5. In the Wagtail admin, go to **Settings → Google tag** and enter your GA4 measurement ID. In Google Analytics, it's under **Admin → Data streams**, in your web stream.

The tag's script is one of the package's static files. On a deployed site, run `collectstatic` after you install or upgrade the package, as for any app's static files.

## See your visit

1. Visit your site while signed out of Wagtail, or in a private window, and open a few pages.
2. In Google Analytics, open **Reports → Realtime**. Your page views appear there, typically within a few minutes.

Nothing there? See [Test your setup and troubleshoot](../how-to/test-and-troubleshoot.md).

## Send your first event

Add two attributes to any link or button in a template:

```html
<a href="/pricing/"
   data-google-tag-event="select_content"
   data-google-tag-params='{"content_type": "cta", "content_id": "pricing-hero"}'>
  See pricing
</a>
```

Click it on your site, then select `select_content` in Realtime to see its parameters.

## Next

- Finish the setup on Google's side: [Set up Google Analytics](../how-to/set-up-google-analytics.md).
- Decide who gets the tag and what it does before a visitor has chosen: [Who is tracked](../explanation/who-is-tracked.md) and [Consent](../explanation/consent.md).
- If you have a consent banner: [Connect a consent banner](../how-to/connect-a-consent-banner.md).
