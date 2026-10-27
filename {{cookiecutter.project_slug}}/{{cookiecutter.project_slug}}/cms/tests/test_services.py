import pytest
from wagtail.models import Site

from {{ cookiecutter.project_slug }}.cms.models import HomePage
from {{ cookiecutter.project_slug }}.cms.services import HomePageService

pytestmark = pytest.mark.django_db


def test_get_or_create_default_reuses_migrated_home_page():
    home, created = HomePageService.get_or_create_default()

    assert not created
    assert HomePage.objects.get() == home
    assert Site.objects.get(is_default_site=True).root_page_id == home.pk


def test_get_or_create_default_is_idempotent():
    HomePageService.get_or_create_default()
    HomePageService.get_or_create_default()

    assert HomePage.objects.count() == 1
    assert Site.objects.filter(is_default_site=True).count() == 1


def test_get_or_create_default_recreates_deleted_home_page():
    HomePage.objects.get().delete()

    home, created = HomePageService.get_or_create_default(site_name="Example")

    assert created
    site = Site.objects.get(is_default_site=True)
    assert site.root_page_id == home.pk
    assert site.site_name == "Example"
