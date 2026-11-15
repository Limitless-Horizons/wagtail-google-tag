# Keep secrets out of page addresses

Google Analytics records the address of every page it sees. Some addresses hold something Google shouldn't get: a signed download link, an unsubscribe or password-reset link, an order number. Whoever has such a link can use it, and Google's own rules say [the URL path must be free of personal information](https://support.google.com/analytics/answer/6366371).

You don't have to take analytics off those pages. Give the tag the address to report instead:

```django
{% google_tag page_location="/downloads/link/" %}
```

Google Analytics then records `https://example.com/downloads/link/` for the page view and for every event on that page, in place of the browser's address. Leave the argument out, or empty, and nothing changes.

## One tag in a base template

Most sites have `{% google_tag %}` once, in a base template. Pass it a variable that only the views with a secret in their address set:

```django
{# base.html #}
{% google_tag page_location=analytics_location %}
```

```python
# views.py
def download(request, token):
    ...
    return TemplateResponse(
        request,
        "downloads/link.html",
        {"analytics_location": "/downloads/link/", ...},
    )
```

On every other page the variable is unset, so the tag reports the browser's address as before.

## What to pass

- **A path** (`/downloads/link/`) is completed with the request's scheme and host. Google requires a full URL.
- **A full URL** is used as it is.
- The address doesn't have to exist on your site. It's a name for the page in your reports, so use the same one for every visitor.
- Google reads up to 1,000 characters.

## The referrer needs its own fix

The page a visitor opens next tells Google Analytics where they came from, and browsers send the full previous address to pages on the same site. Limit that on the response of the page with the secret:

```python
response.headers["Referrer-Policy"] = "strict-origin"
```

The next page then learns only your site's address. Django's `SecurityMiddleware` leaves a `Referrer-Policy` header that's already set.

Use `strict-origin`, not `no-referrer`, on a page with a form: Django's CSRF protection checks where a form was sent from, and with `no-referrer` it refuses the form.

## What this doesn't cover

- **Query parameters.** Google Analytics can redact named query parameters and email addresses itself: Admin → Data streams → your stream → Redact data. That setting doesn't reach a secret in the path, which is what `page_location` is for.
- **Your server's own logs,** which record the real address of every request.

## How it works

The tag queues `gtag('set', 'page_location', …)` before Google's script starts, which is how Google documents overriding it. We checked it against Google's tag: the page view and later events carry the address you gave, and the browser's address isn't sent.
