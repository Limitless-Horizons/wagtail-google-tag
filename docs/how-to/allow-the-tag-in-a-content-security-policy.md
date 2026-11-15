# Allow the tag in a Content Security Policy

If your site has a Content Security Policy, allow Google's tag in it. Google lists the sources Google Analytics needs in its [Content Security Policy guide](https://developers.google.com/tag-platform/security/guides/csp#google_analytics): `https://www.googletagmanager.com` for scripts, and more for images and connections. The package itself uses no inline scripts.
