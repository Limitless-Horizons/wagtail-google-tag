"""
What the {% google_tag %} template tag renders: whether Google's tag loads for
this request, and the configuration the browser script gets.
"""

from django.conf import settings
from django.utils.text import capfirst
from wagtail.models import Page

from .models import GoogleTagSettings


# The European Economic Area (the EU, Iceland, Liechtenstein and Norway), the
# UK and Switzerland, as ISO 3166-1 codes for Consent Mode's "region".
EUROPE = (
    # EU
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GR", "HR",
    "HU", "IE", "IT", "LT", "LU", "LV", "MT", "NL", "PL", "PT", "RO", "SE", "SI",
    "SK",
    # Rest of the EEA
    "IS", "LI", "NO",
    # UK and Switzerland
    "GB", "CH",
)  # fmt: skip

# How long Google's tag waits for a consent banner's update in Europe, in ms.
WAIT_FOR_UPDATE = 500

AD_SIGNALS = ("ad_storage", "ad_user_data", "ad_personalization")


def get_settings(request):
    """This site's settings, or the defaults when the request has no site."""
    try:
        return GoogleTagSettings.for_request(request)
    except GoogleTagSettings.DoesNotExist:
        return GoogleTagSettings()


def get_measurement_id(site_settings):
    """The site's measurement ID, or the WAGTAIL_GOOGLE_TAG_MEASUREMENT_ID
    setting when the site has none."""
    return site_settings.measurement_id or getattr(
        settings, "WAGTAIL_GOOGLE_TAG_MEASUREMENT_ID", ""
    )


def default_page_params(page):
    """The page_view parameters for a page without get_google_tag_params():
    its page type as GA's content group."""
    model = page.specific_class or type(page)
    return {"content_group": str(capfirst(model._meta.verbose_name))}


def page_params(page):
    get_params = getattr(page, "get_google_tag_params", None)
    if get_params is None:
        return default_page_params(page)
    return dict(get_params())


def consent_defaults(site_settings):
    """Consent Mode defaults: analytics granted, ad signals denied unless the
    site uses Google Ads, and everything denied in Europe if the site says so.
    Google applies the most specific region that matches the visitor."""
    ads = "granted" if site_settings.uses_google_ads else "denied"
    defaults = [{"analytics_storage": "granted", **dict.fromkeys(AD_SIGNALS, ads)}]
    if site_settings.deny_analytics_in_europe:
        defaults.append(
            {
                "analytics_storage": "denied",
                **dict.fromkeys(AD_SIGNALS, "denied"),
                "region": list(EUROPE),
                "wait_for_update": WAIT_FOR_UPDATE,
            }
        )
    return defaults


def is_signed_in(request):
    user = getattr(request, "user", None)
    return bool(user and user.is_authenticated)


def tag_config(context, overrides):
    """The browser script's configuration. "id" is None when the tag doesn't
    load: no measurement ID, a preview, or a signed-in user who isn't tracked."""
    request = context.get("request")
    if request is None:
        return {"id": None}

    site_settings = get_settings(request)
    measurement_id = get_measurement_id(site_settings)
    if (
        not measurement_id
        or getattr(request, "is_preview", False)
        or (is_signed_in(request) and not site_settings.track_signed_in_users)
    ):
        return {"id": None}

    page = context.get("page")
    params = page_params(page) if isinstance(page, Page) else {}
    params.update(overrides)
    if site_settings.debug_mode:
        params["debug_mode"] = True

    return {
        "id": measurement_id,
        "consent": consent_defaults(site_settings),
        "params": params,
        "ads": site_settings.uses_google_ads,
        "contactLinks": site_settings.track_contact_links,
    }
