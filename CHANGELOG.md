# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-10

### Added

- Google tag settings for each site in the Wagtail admin (Settings → Google tag): measurement ID, Europe consent defaults, Google Ads, signed-in users, email and phone links, and debug mode.
- `WAGTAIL_GOOGLE_TAG_MEASUREMENT_ID`, a Django setting used when a site has no measurement ID.
- The `{% google_tag %}` template tag, which loads Google's tag with Consent Mode defaults and the page's data, except in previews and for signed-in users.
- Page data from a page model's `get_google_tag_params()`, or the page type as GA's content group.
- `window.wagtailGoogleTag.track()` and `window.wagtailGoogleTag.consent()`, and the `wagtail-cookie-consent:change` event for consent banners.
- Click events from `data-google-tag-event` and `data-google-tag-params`, and `contact_link_click` for email and phone links.
- Support for Wagtail 7.4, 8.0 and 8.1.

[Unreleased]: https://github.com/Limitless-Horizons/wagtail-google-tag/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Limitless-Horizons/wagtail-google-tag/releases/tag/v0.1.0
