from django import template

from ..tag import tag_config


register = template.Library()


@register.inclusion_tag("wagtail_google_tag/google_tag.html", takes_context=True)
def google_tag(context, **params):
    """Google's tag, with Consent Mode defaults and the page's data, and the
    window.wagtailGoogleTag script API. Keyword arguments add page_view
    parameters, for templates without a Wagtail page:
    {% google_tag content_group="Not found" %}."""
    return {"config": tag_config(context, params)}
