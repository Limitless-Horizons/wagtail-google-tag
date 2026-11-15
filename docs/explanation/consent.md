# Consent

## What the tag starts with

Before a visitor has made a choice, Google's tag starts with these Consent Mode defaults:

| Visitors | Analytics | Advertising signals |
|---|---|---|
| In the European Economic Area, the UK and Switzerland | Denied | Denied |
| Everywhere else | Granted | Denied, unless "Site uses Google Ads" is on |

Google works out where a visitor is. Denied analytics means no analytics cookies: Google Analytics receives only cookieless pings, which Google says can't directly identify an individual, and uses them to model the data that's missing. To start with analytics granted everywhere, turn off **Deny analytics by default in Europe**.

This is what Google calls advanced consent mode: the tag loads for every visitor and adjusts to their consent, rather than staying off until they agree. It keeps the most measurement Consent Mode allows. A cookieless ping still reaches Google, so check that this fits the rules that apply to your site.

## When a visitor chooses

A consent banner updates these defaults with the visitor's choice: see [Connect a consent banner](../how-to/connect-a-consent-banner.md).

When a visitor refuses or withdraws analytics, the package also deletes Google Analytics' cookies (`_ga` and those starting with `_ga_`), which Google's tag would otherwise leave in place, and clears the [User-ID](../how-to/set-a-user-id.md) if your site set one.

## Google Analytics' own consent settings

Google Analytics has two settings of its own that touch these defaults. They're in the property's Google tag settings, under **Admin → Data streams →** your stream **→ Configure tag settings**:

- **Override consent mode defaults:** leave it unset. If it's set, it replaces the defaults above.
- **Manage default consent settings:** choose "No. Do not automatically mark this data as consented."

## Consent and "Leave out of tracking"

These do different jobs, and neither overrides the other: see [Who is tracked](who-is-tracked.md).
