# Template tag

```django
{% load wagtail_google_tag %}
{% google_tag %}
```

`{% google_tag %}` renders Google's tag for the current site, with its Consent Mode defaults, and the package's script. Put it near the top of `<head>`, once per page.

It needs the request in the template context (`django.template.context_processors.request`).

## When it loads nothing

The tag's own script is always there, so [`window.wagtailGoogleTag`](script-api.md) works on every page. Google's tag isn't loaded, and nothing is sent, when:

- the site's measurement ID is blank;
- the page is a Wagtail preview;
- the visitor has a role checked under [Leave out of tracking](settings.md#leave-out-of-tracking);
- the template context has no request.

## Arguments

| Argument | Default | What it does |
|---|---|---|
| `page_location` | The browser's address | The address Google Analytics records for this page, for the page view and every event on it. A path (`/downloads/link/`) is completed with the request's scheme and host; a full URL is used as it is. Empty or missing means the browser's address. See [Keep secrets out of page addresses](../how-to/keep-secrets-out-of-page-addresses.md). |

The tag takes no other arguments. Parameters go on events, not on the tag: see [Page views](../explanation/page-views.md).
