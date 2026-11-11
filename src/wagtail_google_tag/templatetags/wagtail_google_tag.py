from django import template

from ..tag import tag_config


register = template.Library()


@register.inclusion_tag("wagtail_google_tag/google_tag.html", takes_context=True)
def google_tag(context):
    """Google's tag, with Consent Mode defaults, and the window.wagtailGoogleTag
    script API."""
    return {"config": tag_config(context)}
