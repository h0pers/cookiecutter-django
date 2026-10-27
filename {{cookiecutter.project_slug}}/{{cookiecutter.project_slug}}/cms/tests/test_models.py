from http import HTTPStatus

import pytest
from wagtail.models import Page

from {{ cookiecutter.project_slug }}.cms.models import HomePage

pytestmark = pytest.mark.django_db


def test_migration_serves_home_page_at_root(client):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert "cms/home_page.html" in [t.name for t in response.templates]


def test_home_page_only_under_tree_root():
    home = HomePage.objects.get()

    assert not HomePage.can_create_at(home)
    assert HomePage.parent_page_types == ["wagtailcore.Page"]


def test_only_one_home_page():
    root = Page.get_first_root_node()

    assert not HomePage.can_create_at(root)
