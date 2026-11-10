from django.apps import apps
from django.core.checks import Error, register


@register()
def settings_app_installed(app_configs, **kwargs):
    if apps.is_installed("wagtail.contrib.settings"):
        return []
    return [
        Error(
            "wagtail_google_tag needs wagtail.contrib.settings.",
            hint='Add "wagtail.contrib.settings" to INSTALLED_APPS.',
            id="wagtail_google_tag.E001",
        )
    ]
