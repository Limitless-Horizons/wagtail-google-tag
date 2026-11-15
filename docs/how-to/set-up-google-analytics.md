# Set up Google Analytics

These are set in Google Analytics, not in Wagtail. All of them are under **Admin** in your property.

1. **Data retention.** Under **Data collection and modification → Data retention**, choose how long Google Analytics keeps event data: 2 months, which is the default, or 14 months. Match what your privacy notice says.
2. **Enhanced measurement.** Under **Data collection and modification → Data streams →** your stream, check that **Enhanced measurement** is on. It's what sends scrolls, outbound clicks and site search. The search page in Wagtail's project template works as it is: its `?query=` is one of the parameters Google looks for.
3. **Key events.** Under **Data display → Events**, mark the events that count as results for you, such as `generate_lead`. An event appears there once Google Analytics has received it. To set one up before that, create the event there under its exact name, with **Create with code** and no default value.
4. **Custom dimensions.** A parameter on one of your events shows in reports only after you create a custom dimension for it. Under **Data display → Custom definitions**, create one with the scope **Event** for each parameter you want to report on. For the package's own event, that's `link_type` on `contact_link_click`. Type the parameter's name if the list doesn't offer it. A dimension fills in only from the day you create it.
5. **Google tag settings.** Under **Data collection and modification → Data streams →** your stream **→ Configure tag settings**:
   - **Allow user-provided data capabilities:** when it's on, Google's tag may look for email addresses on your pages. Turn it off if no email address should reach Google Analytics.
   - **Override consent mode defaults:** leave it unset, as in [Consent](../explanation/consent.md).
   - **Manage default consent settings:** choose "No. Do not automatically mark this data as consented."

   Some of these are behind **Show more**. If Google asks you to publish a new version, do: the settings don't apply until then.
6. **Reporting identity,** if your site sets a [User-ID](set-a-user-id.md). Under **Data display → Reporting identity**, choose **Blended** or **Observed**: both use the User-ID. To follow one person, use the **User explorer** technique under **Explore**; it's also where you delete one person's data if they ask.
7. **Check that it works,** as in [Test your setup and troubleshoot](test-and-troubleshoot.md).
