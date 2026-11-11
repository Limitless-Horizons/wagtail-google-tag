# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-11

### Added

- **Leave out of tracking**, a list of roles whose members get no tag: anyone signed in, administrators, signed-in users with no group, and each group. With nothing checked, everyone is tracked.

### Changed

- Google's tag is installed the way Google documents it now: its script comes from `gtm.js`, and the deprecated `config` command isn't used. The tags of newer Google Analytics properties ignore `config`, so 0.1.0 behaved differently from one property to another.
- Signed-in users are tracked unless a site leaves their role out. In 0.1.0 they weren't tracked unless a site turned that on.
- Each switch's help text says what turning it on does.

### Removed

- Data on the page view: `get_google_tag_params()` on page models, the default `content_group`, parameters on `{% google_tag %}`, and `wagtail_google_tag.tag.default_page_params()`. The tags of newer Google Analytics properties ignore parameters a page adds to the page view. Google's tag sends the page view as before.
- The **Track signed-in users** switch, replaced by **Leave out of tracking**. A site that had it off gets **Anyone signed in** checked, so its behavior doesn't change.
- The **Debug mode** switch. Google Analytics' Realtime report shows page views and events without it.
- The `WAGTAIL_GOOGLE_TAG_MEASUREMENT_ID` Django setting. A site's measurement ID comes from the Wagtail admin only.

## [0.1.0] - 2026-11-10

### Added

- Google tag settings for each site in the Wagtail admin (Settings → Google tag): measurement ID, Europe consent defaults, Google Ads, signed-in users, email and phone links, and debug mode.
- `WAGTAIL_GOOGLE_TAG_MEASUREMENT_ID`, a Django setting used when a site has no measurement ID.
- The `{% google_tag %}` template tag, which loads Google's tag with Consent Mode defaults and the page's data, except in previews and for signed-in users.
- Page data from a page model's `get_google_tag_params()`, or the page type as GA's content group.
- `window.wagtailGoogleTag.track()` and `window.wagtailGoogleTag.consent()`, and the `wagtail-cookie-consent:change` event for consent banners.
- Click events from `data-google-tag-event` and `data-google-tag-params`, and `contact_link_click` for email and phone links.
- Support for Wagtail 7.4, 8.0 and 8.1.

[Unreleased]: https://github.com/Limitless-Horizons/wagtail-google-tag/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Limitless-Horizons/wagtail-google-tag/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Limitless-Horizons/wagtail-google-tag/releases/tag/v0.1.0
