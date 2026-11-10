from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailGoogleTagAppConfig(AppConfig):
    label = "wagtail_google_tag"
    name = "wagtail_google_tag"
    verbose_name = _("Google tag")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import checks  # noqa: F401
