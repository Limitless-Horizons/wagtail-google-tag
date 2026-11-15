from django import template

from ..tag import tag_config


register = template.Library()


@register.inclusion_tag("wagtail_google_tag/google_tag.html", takes_context=True)
def google_tag(context, page_location=None):
    """Google's tag, with Consent Mode defaults, and the window.wagtailGoogleTag
    script API.

    ``page_location`` is the address Google Analytics records for this page,
    in place of the browser's: a path or a full URL. Leave it out, or empty,
    for the browser's own address."""
    return {"config": tag_config(context, page_location=page_location)}
