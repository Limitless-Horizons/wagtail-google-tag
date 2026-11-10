from django.db import models
from wagtail.models import Page

from wagtail_google_tag.tag import default_page_params


class TopicPage(Page):
    """A page that adds its own Google tag parameter."""

    topic = models.CharField(max_length=50, blank=True)

    def get_google_tag_params(self):
        return {**default_page_params(self), "article_topic": self.topic}


class PlainPage(Page):
    """A page with the default Google tag parameters."""
