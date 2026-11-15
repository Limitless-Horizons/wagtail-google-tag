# Test your setup and troubleshoot

## Test

Visit your site, click around, and watch Google Analytics' **Realtime** report (**Reports → Realtime**). Google gives Realtime's delay as typically a few minutes, with no guarantee. Select an event there to see the parameters sent with it. If your own role is checked under **Leave out of tracking**, visit while signed out of Wagtail.

## Troubleshoot

- **No tag on the page:** the measurement ID is blank, your role is left out, the page is a preview, or `collectstatic` hasn't run. Run `python manage.py check` too: it warns when the request isn't in the template context.
- **Nothing in Realtime:** wait a few minutes, and turn off any ad blocker or tracking protection in your browser.
- **A parameter isn't in reports:** create a custom dimension for it (item 4 of [Set up Google Analytics](set-up-google-analytics.md)).
- **A Google tag setting has no effect:** publish the new version (item 5 of [Set up Google Analytics](set-up-google-analytics.md)).
- **Little data from Europe:** expected while analytics is denied by default. See [Consent](../explanation/consent.md).
