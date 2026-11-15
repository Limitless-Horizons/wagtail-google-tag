# Add the tag to templates outside your base template

A template that doesn't extend your base template, such as a 404 page, needs the tag too:

```django
{% load wagtail_google_tag %}
...
{% google_tag %}
```
