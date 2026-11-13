# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2026-11-13

### Added

- `window.wagtailGoogleTag.user(id)` sets Google Analytics' User-ID for the events that follow, and `user(null)` clears it. The User-ID is also cleared when a visitor refuses or withdraws analytics.
- README: a User-ID section with Google's rules for the feature, and a Reporting identity item in the Google Analytics setup checklist.

## [0.2.3] - 2026-11-12

### Changed

- README: a screenshot of the settings in the Wagtail admin.

## [0.2.2] - 2026-11-11

### Fixed

- A visitor's stored consent choice now applies to the page view of each later page. Google's tag sends the page view as soon as it starts, so outside Europe a stored refusal used to reach it too late. Google's tag now waits half a second for the choice everywhere, as it already did in Europe.

### Added

- When a visitor refuses or withdraws analytics, Google Analytics' cookies (`_ga` and those starting with `_ga_`) are deleted.
- A system check that warns when the request isn't in the template context.

### Changed

- `LICENSE` names the copyright holder, and the package metadata names the author.
- README: a link to `AGENTS.md`, and `wagtail-cookie-consent` is no longer "in development".

## [0.2.1] - 2026-11-11

### Changed

- The help text at the top of **Leave out of tracking** changed.
- README: a Troubleshooting section, and more detail in the Google Analytics setup checklist.

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

[Unreleased]: https://github.com/Limitless-Horizons/wagtail-google-tag/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/Limitless-Horizons/wagtail-google-tag/compare/v0.2.3...v0.3.0
[0.2.3]: https://github.com/Limitless-Horizons/wagtail-google-tag/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/Limitless-Horizons/wagtail-google-tag/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/Limitless-Horizons/wagtail-google-tag/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/Limitless-Horizons/wagtail-google-tag/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Limitless-Horizons/wagtail-google-tag/releases/tag/v0.1.0
