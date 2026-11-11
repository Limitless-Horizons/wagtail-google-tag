"""
What the {% google_tag %} template tag renders: whether Google's tag loads for
this request, and the configuration the browser script gets.
"""

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


def tag_config(context):
    """The browser script's configuration. "id" is None when the tag doesn't
    load: no measurement ID, a preview, or a visitor with a role the site
    leaves out of tracking."""
    request = context.get("request")
    if request is None:
        return {"id": None}

    site_settings = get_settings(request)
    if (
        not site_settings.measurement_id
        or getattr(request, "is_preview", False)
        or site_settings.leaves_out(getattr(request, "user", None))
    ):
        return {"id": None}

    return {
        "id": site_settings.measurement_id,
        "consent": consent_defaults(site_settings),
        "ads": site_settings.uses_google_ads,
        "contactLinks": site_settings.track_contact_links,
    }
