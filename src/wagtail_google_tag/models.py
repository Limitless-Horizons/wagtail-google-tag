import re

from django import forms
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
            "Analytics, it's under Admin, Data streams. Leave it blank for no tag."
        ),
    )
    deny_analytics_in_europe = models.BooleanField(
        _("deny analytics by default in Europe"),
        default=True,
        help_text=_(
            "When this is on, visitors in the European Economic Area, the UK and "
            "Switzerland start with analytics and advertising signals denied, and "
            "get no analytics cookies until they agree, for example through a "
            "consent banner."
        ),
    )
    uses_google_ads = models.BooleanField(
        _("site uses Google Ads"),
        default=False,
        help_text=_(
            "When this is on, Google's advertising signals are granted by default "
            "outside Europe, and a consent banner's marketing choice sets them. "
            "When it's off, they're denied for every visitor."
        ),
    )
    exclude_signed_in = models.BooleanField(
        _("anyone signed in"),
        default=False,
        help_text=_(
            "When this is on, no signed-in user gets the tag. It overrides the "
            "rest of this list."
        ),
    )
    exclude_administrators = models.BooleanField(
        _("administrators"),
        default=False,
        help_text=_("When this is on, users with Administrator status get no tag."),
    )
    exclude_no_group = models.BooleanField(
        _("signed in, with no group"),
        default=False,
        help_text=_(
            "When this is on, signed-in users who belong to no group get no tag."
        ),
    )
    exclude_groups = models.ManyToManyField(
        "auth.Group",
        verbose_name=_("groups"),
        blank=True,
        related_name="+",
        help_text=_("Members of a checked group get no tag."),
    )
    track_contact_links = models.BooleanField(
        _("track email and phone links"),
        default=True,
        help_text=_(
            "When this is on, clicks on email and phone links send a "
            "contact_link_click event. The address or number itself is never sent."
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
                FieldPanel("exclude_signed_in"),
                FieldPanel("exclude_administrators"),
                FieldPanel("exclude_no_group"),
                FieldPanel("exclude_groups", widget=forms.CheckboxSelectMultiple),
            ],
            heading=_("Leave out of tracking"),
            help_text=_(
                "Visitors with a checked role get no tag. With nothing checked, "
                "everyone is tracked. Visitors who aren't signed in are always "
                "tracked."
            ),
        ),
        FieldPanel("track_contact_links"),
    ]

    class Meta:
        verbose_name = _("Google tag")
        verbose_name_plural = _("Google tag")

    def save(self, *args, **kwargs):
        self.measurement_id = self.measurement_id.strip().upper()
        super().save(*args, **kwargs)

    def leaves_out(self, user):
        """Whether this user holds a role the site leaves out of tracking.
        Visitors who aren't signed in are never left out."""
        if not (user and user.is_authenticated):
            return False
        if self.exclude_signed_in:
            return True
        if self.exclude_administrators and getattr(user, "is_superuser", False):
            return True
        if not hasattr(user, "groups"):
            return False
        group_ids = set(user.groups.values_list("pk", flat=True))
        if not group_ids:
            return self.exclude_no_group
        if self.pk is None:
            return False
        left_out = set(self.exclude_groups.values_list("pk", flat=True))
        return bool(group_ids & left_out)
