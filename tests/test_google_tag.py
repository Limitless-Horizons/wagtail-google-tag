import json
import re

import pytest

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.core.checks import run_checks
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.template import Context, Template, TemplateSyntaxError
from django.test import RequestFactory, override_settings
from wagtail.models import Site

from wagtail_google_tag.models import GoogleTagSettings
from wagtail_google_tag.tag import EUROPE
from wagtail_google_tag.test.models import PlainPage


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


def test_no_tag_without_request():
    html = Template("{% load wagtail_google_tag %}{% google_tag %}").render(Context())
    assert config_in(html) == {"id": None}


def test_no_site_uses_defaults(tag_settings):
    request = anonymous_request()
    request.META["HTTP_HOST"] = "unknown.example"
    Site.objects.update(is_default_site=False)
    assert config_in(render("{% google_tag %}", request)) == {"id": None}


# Who is left out of tracking


def tag_loads_for(client, page, user=None):
    if user is None:
        client.logout()
    else:
        client.force_login(user)
    return config_in(client.get(page.url).content.decode())["id"] is not None


@pytest.fixture
def people():
    users = get_user_model().objects
    editors = Group.objects.get_or_create(name="Editors")[0]
    members = Group.objects.get_or_create(name="Members")[0]
    editor = users.create_user("editor")
    editor.groups.add(editors)
    member = users.create_user("member")
    member.groups.add(members)
    both = users.create_user("both")
    both.groups.add(editors, members)
    return {
        "editors": editors,
        "members": members,
        "editor": editor,
        "member": member,
        "both": both,
        "nogroup": users.create_user("nogroup"),
        "admin": users.create_superuser("admin"),
        "admin_editor": users.create_superuser("admin_editor"),
    }


def test_everyone_is_tracked_with_nothing_checked(
    client, tag_settings, plain_page, people
):
    for name in ("editor", "member", "both", "nogroup", "admin"):
        assert tag_loads_for(client, plain_page, people[name]), name
    assert tag_loads_for(client, plain_page)


def test_a_checked_group_is_left_out(client, tag_settings, plain_page, people):
    tag_settings.exclude_groups.add(people["editors"])
    assert not tag_loads_for(client, plain_page, people["editor"])
    assert tag_loads_for(client, plain_page, people["member"])
    assert tag_loads_for(client, plain_page, people["nogroup"])
    assert tag_loads_for(client, plain_page, people["admin"])
    assert tag_loads_for(client, plain_page)


def test_any_checked_group_leaves_out_a_user_in_several(
    client, tag_settings, plain_page, people
):
    tag_settings.exclude_groups.add(people["members"])
    assert not tag_loads_for(client, plain_page, people["both"])
    assert tag_loads_for(client, plain_page, people["editor"])


def test_administrators_left_out(client, tag_settings, plain_page, people):
    people["admin_editor"].groups.add(people["editors"])
    tag_settings.exclude_administrators = True
    tag_settings.save()
    assert not tag_loads_for(client, plain_page, people["admin"])
    assert not tag_loads_for(client, plain_page, people["admin_editor"])
    assert tag_loads_for(client, plain_page, people["editor"])
    assert tag_loads_for(client, plain_page, people["nogroup"])


def test_signed_in_with_no_group_left_out(client, tag_settings, plain_page, people):
    tag_settings.exclude_no_group = True
    tag_settings.save()
    assert not tag_loads_for(client, plain_page, people["nogroup"])
    assert tag_loads_for(client, plain_page, people["editor"])
    assert tag_loads_for(client, plain_page, people["member"])
    assert tag_loads_for(client, plain_page)


def test_anyone_signed_in_overrides_the_list(client, tag_settings, plain_page, people):
    tag_settings.exclude_signed_in = True
    tag_settings.save()
    for name in ("editor", "member", "both", "nogroup", "admin"):
        assert not tag_loads_for(client, plain_page, people[name]), name
    assert tag_loads_for(client, plain_page)


def test_visitors_who_are_not_signed_in_are_always_tracked(
    client, tag_settings, plain_page, people
):
    tag_settings.exclude_signed_in = True
    tag_settings.exclude_administrators = True
    tag_settings.exclude_no_group = True
    tag_settings.save()
    tag_settings.exclude_groups.add(people["editors"], people["members"])
    assert tag_loads_for(client, plain_page)


def test_settings_that_were_never_saved_leave_nobody_out(people):
    for name in ("editor", "nogroup", "admin"):
        assert GoogleTagSettings().leaves_out(people[name]) is False


# More than one site


@override_settings(ALLOWED_HOSTS=["*"])
def test_each_site_gets_its_own_settings(
    client, tag_settings, site, plain_page, people
):
    other_root = PlainPage(title="Other", slug="other")
    site.root_page.add_child(instance=other_root)
    other = Site.objects.create(hostname="other.example", root_page=other_root)
    blank_root = PlainPage(title="Blank", slug="blank")
    site.root_page.add_child(instance=blank_root)
    Site.objects.create(hostname="blank.example", root_page=blank_root)

    other_settings = GoogleTagSettings.for_site(other)
    other_settings.measurement_id = "G-OTHER1"
    other_settings.save()
    other_settings.exclude_groups.add(people["editors"])

    def config(host, user=None, path="/"):
        client.logout()
        if user:
            client.force_login(user)
        return config_in(client.get(path, HTTP_HOST=host).content.decode())

    here = {"host": site.hostname, "path": plain_page.url}
    assert config(**here)["id"] == "G-TEST123"
    assert config("other.example")["id"] == "G-OTHER1"
    assert config("blank.example") == {"id": None}
    # The other site leaves editors out; this one doesn't.
    assert config("other.example", people["editor"]) == {"id": None}
    assert config(user=people["editor"], **here)["id"] == "G-TEST123"


# Measurement ID


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
        "wait_for_update": 500,
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


# What the page hands the script


def test_config_has_no_page_view_parameters(client, tag_settings, plain_page):
    config = config_in(client.get(plain_page.url).content.decode())
    assert set(config) == {"id", "consent", "ads", "contactLinks"}


def test_template_tag_takes_no_parameters(tag_settings):
    with pytest.raises(TemplateSyntaxError):
        render('{% google_tag content_group="Not found" %}', anonymous_request())


def test_tag_renders_without_a_page(tag_settings):
    html = render("{% google_tag %}", anonymous_request())
    assert config_in(html)["id"] == "G-TEST123"


@override_settings(WAGTAIL_GOOGLE_TAG_MEASUREMENT_ID="G-FALLBACK")
def test_no_fallback_setting(client, plain_page):
    config = config_in(client.get(plain_page.url).content.decode())
    assert config == {"id": None}


def test_config_is_escaped(client, tag_settings, plain_page):
    GoogleTagSettings.objects.filter(pk=tag_settings.pk).update(
        measurement_id="</script><script>alert(1)"
    )
    html = client.get(plain_page.url).content.decode()
    assert "<script>alert(1)" not in html
    assert config_in(html)["id"].startswith("</script>")


def test_contact_links_setting(client, tag_settings, plain_page):
    assert config_in(client.get(plain_page.url).content.decode())["contactLinks"]
    tag_settings.track_contact_links = False
    tag_settings.save()
    assert not config_in(client.get(plain_page.url).content.decode())["contactLinks"]


# Admin


def test_settings_page_in_admin(client, site):
    admin = get_user_model().objects.create_superuser("admin")
    client.force_login(admin)
    url = f"/admin/settings/wagtail_google_tag/googletagsettings/{site.pk}/"
    response = client.get(url)
    assert response.status_code == 200
    content = response.content.decode()
    assert "Measurement ID" in content
    assert "Leave out of tracking" in content
    editors = Group.objects.get_or_create(name="Editors")[0]

    response = client.post(
        url,
        {
            "measurement_id": "g-saved1",
            "deny_analytics_in_europe": "on",
            "track_contact_links": "on",
            "exclude_administrators": "on",
            "exclude_groups": [editors.pk],
        },
    )
    assert response.status_code == 302
    saved = GoogleTagSettings.for_site(site)
    assert saved.measurement_id == "G-SAVED1"
    assert saved.deny_analytics_in_europe is True
    assert saved.uses_google_ads is False
    assert saved.exclude_administrators is True
    assert saved.exclude_signed_in is False
    assert list(saved.exclude_groups.all()) == [editors]


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


def test_request_context_processor_check(settings):
    templates = [dict(engine) for engine in settings.TEMPLATES]
    templates[0]["OPTIONS"] = {
        "context_processors": ["django.contrib.auth.context_processors.auth"]
    }
    settings.TEMPLATES = templates
    assert [e.id for e in run_checks() if e.id.startswith("wagtail_google_tag")] == [
        "wagtail_google_tag.W001"
    ]


# Moving over from 0.1


@pytest.mark.django_db(transaction=True)
def test_migration_carries_over_the_signed_in_switch():
    app = "wagtail_google_tag"
    executor = MigrationExecutor(connection)
    executor.migrate([(app, "0001_initial")])
    old = executor.loader.project_state([(app, "0001_initial")]).apps
    old_settings = old.get_model(app, "GoogleTagSettings")
    old_site = old.get_model("wagtailcore", "Site")
    page = old.get_model("wagtailcore", "Page").objects.first()
    off = old_site.objects.create(hostname="off.example", root_page=page)
    on = old_site.objects.create(hostname="on.example", root_page=page)
    old_settings.objects.create(site=off, track_signed_in_users=False)
    old_settings.objects.create(site=on, track_signed_in_users=True)

    executor = MigrationExecutor(connection)
    executor.migrate([(app, "0002_leave_out_of_tracking")])

    assert GoogleTagSettings.objects.get(site_id=off.pk).exclude_signed_in is True
    assert GoogleTagSettings.objects.get(site_id=on.pk).exclude_signed_in is False
