import re

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


measurement_id_validator = RegexValidator(
    r"^G-[A-Z0-9]+$",
    _("Enter a GA4 measurement ID, like G-A1B2C3D4E5."),
    flags=re.IGNORECASE,
)


@register_setting(icon="tag")
class GoogleTagSettings(BaseSiteSetting):
    measurement_id = models.CharField(
        _("measurement ID"),
        max_length=20,
        blank=True,
        validators=[measurement_id_validator],
        help_text=_(
            "The GA4 measurement ID for this site, like G-A1B2C3D4E5. In Google "
            "Analytics, it's under Admin, Data streams. Leave it blank for no tag, "
            "unless the site's configuration supplies a default."
        ),
    )
    deny_analytics_in_europe = models.BooleanField(
        _("deny analytics by default in Europe"),
        default=True,
        help_text=_(
            "Visitors in the European Economic Area, the UK and Switzerland get no "
            "analytics cookies until they agree to them, for example through a "
            "consent banner."
        ),
    )
    uses_google_ads = models.BooleanField(
        _("site uses Google Ads"),
        default=False,
        help_text=_(
            "When this is off, Google's advertising signals are denied for every "
            "visitor."
        ),
    )
    track_signed_in_users = models.BooleanField(
        _("track signed-in users"),
        default=False,
        help_text=_(
            "When this is off, visits by signed-in users, such as editors, are "
            "left out of the data."
        ),
    )
    track_contact_links = models.BooleanField(
        _("track email and phone links"),
        default=True,
        help_text=_(
            "Clicks on email and phone links send a contact_link_click event. The "
            "address or number itself is never sent."
        ),
    )
    debug_mode = models.BooleanField(
        _("debug mode"),
        default=False,
        help_text=_(
            "Sends events to DebugView in Google Analytics, for testing. Turn it "
            "off when you're done."
        ),
    )

    panels = [
        FieldPanel("measurement_id"),
        MultiFieldPanel(
            [
                FieldPanel("deny_analytics_in_europe"),
                FieldPanel("uses_google_ads"),
            ],
            heading=_("Consent"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("track_signed_in_users"),
                FieldPanel("track_contact_links"),
                FieldPanel("debug_mode"),
            ],
            heading=_("Tracking"),
        ),
    ]

    class Meta:
        verbose_name = _("Google tag")
        verbose_name_plural = _("Google tag")

    def save(self, *args, **kwargs):
        self.measurement_id = self.measurement_id.strip().upper()
        super().save(*args, **kwargs)
