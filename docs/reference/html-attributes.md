# HTML attributes and events

## Attributes

| Attribute | On | What it does |
|---|---|---|
| `data-google-tag-event` | Any element, usually a link or button | A click on the element, or on anything inside it, sends the event named here. |
| `data-google-tag-params` | The same element | The event's parameters, as JSON. Optional. JSON that can't be read is ignored, and the event is sent without parameters. |

A click sends one event. An email or phone link with its own `data-google-tag-event` sends only that event, not `contact_link_click` as well.

## Events the package sends by itself

| Event | When | Parameters |
|---|---|---|
| `contact_link_click` | A click on a `mailto:` or `tel:` link, when **Track email and phone links** is on | `link_type`: `email` or `phone`. Never the address or number. |

Google's tag sends `page_view`, and Google Analytics' enhanced measurement sends its own events (scrolls, outbound clicks, site search), as set up in Google Analytics.
