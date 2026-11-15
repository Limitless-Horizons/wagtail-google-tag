# Set a User-ID

If your site knows who a visitor is, it can give Google Analytics its own ID for them, so that their visits are counted as one person's across sessions and devices. This is Google Analytics' [User-ID](https://support.google.com/analytics/answer/9213390) feature:

```js
window.wagtailGoogleTag.user("3f6c1a52-9d0e-4c7b-8a41-5e2b7d90c1aa");

// When the visitor is no longer known, or has asked you to stop
window.wagtailGoogleTag.user(null);
```

Call it on each page where you know the visitor, as early as you can. The ID goes on the events that follow, not on the page view Google's tag has already queued; Google Analytics connects a session's earlier events to the ID once it arrives.

The package doesn't decide who a visitor is or whether they've agreed: that's your site's job. Google's rules for the feature are yours to meet:

- **No personal information in the ID.** Use a random ID of your own, never an email address or a name, hashed or not. It can be 256 characters at most.
- **The visitor's consent to connecting their activity.** Google requires it before you join what a visitor did before and after you knew who they were. Agreeing to analytics cookies in a banner isn't that consent. Ask for it separately, in plain words.
- **Notice.** Say in your privacy notice that you use an identifier this way.

When a visitor refuses or withdraws analytics, the package clears the User-ID along with [Google Analytics' cookies](../explanation/consent.md#when-a-visitor-chooses). If they allow analytics again, call `user()` again.

In Google Analytics, choose a reporting identity that uses the User-ID: item 6 of [Set up Google Analytics](set-up-google-analytics.md).
