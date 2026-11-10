import json
import re

import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.checks import run_checks
from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.test import RequestFactory, override_settings
from wagtail.models import Page, Site

from wagtail_google_tag.models import GoogleTagSettings
from wagtail_google_tag.tag import EUROPE
from wagtail_google_tag.test.models import PlainPage, TopicPage


pytestmark = pytest.mark.django_db

CONFIG = re.compile(
    r'<script id="wagtail-google-tag-config" type="application/json">(.*?)</script>',
    re.S,
)


def config_in(html):
    match = CONFIG.search(html)
    assert match, "no Google tag config in the page"
    return json.loads(match.group(1))


@pytest.fixture
def site():
    return Site.objects.get(is_default_site=True)


@pytest.fixture
def tag_settings(site):
    tag_settings = GoogleTagSettings.for_site(site)
    tag_settings.measurement_id = "G-TEST123"
    tag_settings.save()
    return tag_settings


@pytest.fixture
def plain_page(site):
    page = PlainPage(title="Plain", slug="plain")
    site.root_page.add_child(instance=page)
    return page


@pytest.fixture
def topic_page(site):
    page = TopicPage(title="Topic", slug="topic", topic="Strategy")
    site.root_page.add_child(instance=page)
    return page


def render(template, request, **context):
    return Template("{% load wagtail_google_tag %}" + template).render(
        Context({"request": request, **context})
    )


def anonymous_request(path="/"):
    request = RequestFactory().get(path)
    request.user = AnonymousUser()
    return request


# Whether the tag loads


def test_no_tag_without_measurement_id(client, plain_page):
    config = config_in(client.get(plain_page.url).content.decode())
    assert config == {"id": None}


def test_tag_loads_with_measurement_id(client, tag_settings, plain_page):
    html = client.get(plain_page.url).content.decode()
    assert config_in(html)["id"] == "G-TEST123"
    assert "wagtail_google_tag/js/google-tag.js" in html


def test_api_script_is_there_without_the_tag(client, plain_page):
    html = client.get(plain_page.url).content.decode()
    assert "wagtail_google_tag/js/google-tag.js" in html


def test_no_tag_in_previews(tag_settings, plain_page):
    request = anonymous_request()
    request.is_preview = True
    html = render("{% google_tag %}", request, page=plain_page)
    assert config_in(html) == {"id": None}


def test_no_tag_for_signed_in_users(client, tag_settings, plain_page):
    user = get_user_model().objects.create_user("editor")
    client.force_login(user)
    config = config_in(client.get(plain_page.url).content.decode())
    assert config == {"id": None}


def test_signed_in_users_tracked_when_turned_on(client, tag_settings, plain_page):
    tag_settings.track_signed_in_users = True
    tag_settings.save()
    user = get_user_model().objects.create_user("editor")
    client.force_login(user)
    config = config_in(client.get(plain_page.url).content.decode())
    assert config["id"] == "G-TEST123"


def test_no_tag_without_request():
    html = Template("{% load wagtail_google_tag %}{% google_tag %}").render(Context())
    assert config_in(html) == {"id": None}


def test_no_site_uses_defaults(tag_settings):
    request = anonymous_request()
    request.META["HTTP_HOST"] = "unknown.example"
    Site.objects.update(is_default_site=False)
    assert config_in(render("{% google_tag %}", request)) == {"id": None}


# Measurement ID


@override_settings(WAGTAIL_GOOGLE_TAG_MEASUREMENT_ID="G-FALLBACK")
def test_fallback_measurement_id(client, plain_page):
    config = config_in(client.get(plain_page.url).content.decode())
    assert config["id"] == "G-FALLBACK"


@override_settings(WAGTAIL_GOOGLE_TAG_MEASUREMENT_ID="G-FALLBACK")
def test_admin_measurement_id_wins_over_fallback(client, tag_settings, plain_page):
    config = config_in(client.get(plain_page.url).content.decode())
    assert config["id"] == "G-TEST123"


def test_measurement_id_is_saved_in_capitals(tag_settings):
    tag_settings.measurement_id = " g-abc123 "
    tag_settings.save()
    tag_settings.refresh_from_db()
    assert tag_settings.measurement_id == "G-ABC123"


@pytest.mark.parametrize("value", ["UA-12345-1", "G-", "GTM-ABC123", "G-ABC 123"])
def test_measurement_id_must_be_ga4(tag_settings, value):
    tag_settings.measurement_id = value
    with pytest.raises(ValidationError):
        tag_settings.full_clean()


# Consent Mode defaults


def test_consent_defaults(client, tag_settings, plain_page):
    everyone, europe = config_in(client.get(plain_page.url).content.decode())["consent"]
    assert everyone == {
        "analytics_storage": "granted",
        "ad_storage": "denied",
        "ad_user_data": "denied",
        "ad_personalization": "denied",
    }
    assert europe["analytics_storage"] == "denied"
    assert europe["ad_storage"] == "denied"
    assert europe["region"] == list(EUROPE)
    assert europe["wait_for_update"] == 500


def test_europe_covers_eea_uk_and_switzerland():
    assert len(EUROPE) == len(set(EUROPE)) == 32
    assert {"DE", "FR", "IE", "NO", "IS", "LI", "GB", "CH"} <= set(EUROPE)


def test_no_europe_default_when_turned_off(client, tag_settings, plain_page):
    tag_settings.deny_analytics_in_europe = False
    tag_settings.save()
    config = config_in(client.get(plain_page.url).content.decode())
    assert len(config["consent"]) == 1
    assert config["consent"][0]["analytics_storage"] == "granted"


def test_ad_signals_granted_outside_europe_when_site_uses_ads(
    client, tag_settings, plain_page
):
    tag_settings.uses_google_ads = True
    tag_settings.save()
    config = config_in(client.get(plain_page.url).content.decode())
    everyone, europe = config["consent"]
    assert everyone["ad_storage"] == "granted"
    assert europe["ad_storage"] == "denied"
    assert config["ads"] is True


# Page data


def test_default_page_params(client, tag_settings, plain_page):
    config = config_in(client.get(plain_page.url).content.decode())
    assert config["params"] == {"content_group": "Plain page"}


def test_page_params_from_page_model(client, tag_settings, topic_page):
    config = config_in(client.get(topic_page.url).content.decode())
    assert config["params"] == {
        "content_group": "Topic page",
        "article_topic": "Strategy",
    }


def test_page_params_from_template_tag(tag_settings):
    html = render('{% google_tag content_group="Not found" %}', anonymous_request())
    assert config_in(html)["params"] == {"content_group": "Not found"}


def test_template_tag_params_override_page_params(tag_settings, plain_page):
    html = render(
        '{% google_tag content_group="Special" %}', anonymous_request(), page=plain_page
    )
    assert config_in(html)["params"] == {"content_group": "Special"}


def test_page_that_is_not_a_wagtail_page_is_ignored(tag_settings):
    html = render("{% google_tag %}", anonymous_request(), page="not a page")
    assert config_in(html)["params"] == {}


def test_base_page_uses_its_type(tag_settings):
    root = Page.get_first_root_node()
    html = render("{% google_tag %}", anonymous_request(), page=root)
    assert config_in(html)["params"] == {"content_group": "Page"}


def test_debug_mode(client, tag_settings, plain_page):
    tag_settings.debug_mode = True
    tag_settings.save()
    config = config_in(client.get(plain_page.url).content.decode())
    assert config["params"]["debug_mode"] is True


def test_no_debug_mode_param_when_off(client, tag_settings, plain_page):
    config = config_in(client.get(plain_page.url).content.decode())
    assert "debug_mode" not in config["params"]


def test_contact_links_setting(client, tag_settings, plain_page):
    assert config_in(client.get(plain_page.url).content.decode())["contactLinks"]
    tag_settings.track_contact_links = False
    tag_settings.save()
    assert not config_in(client.get(plain_page.url).content.decode())["contactLinks"]


def test_config_is_escaped(tag_settings):
    html = render(
        '{% google_tag content_group="</script><script>alert(1)</script>" %}',
        anonymous_request(),
    )
    assert "<script>alert(1)" not in html
    assert config_in(html)["params"]["content_group"].startswith("</script>")


# Admin


def test_settings_page_in_admin(client, site):
    admin = get_user_model().objects.create_superuser("admin")
    client.force_login(admin)
    url = f"/admin/settings/wagtail_google_tag/googletagsettings/{site.pk}/"
    response = client.get(url)
    assert response.status_code == 200
    assert "Measurement ID" in response.content.decode()

    response = client.post(
        url,
        {
            "measurement_id": "g-saved1",
            "deny_analytics_in_europe": "on",
            "track_contact_links": "on",
        },
    )
    assert response.status_code == 302
    saved = GoogleTagSettings.for_site(site)
    assert saved.measurement_id == "G-SAVED1"
    assert saved.deny_analytics_in_europe is True
    assert saved.uses_google_ads is False


def test_settings_app_check():
    errors = [e for e in run_checks() if e.id.startswith("wagtail_google_tag")]
    assert errors == []
    with override_settings(
        INSTALLED_APPS=["wagtail_google_tag", "django.contrib.contenttypes"]
    ):
        from wagtail_google_tag.checks import settings_app_installed

        assert [e.id for e in settings_app_installed(None)] == [
            "wagtail_google_tag.E001"
        ]
