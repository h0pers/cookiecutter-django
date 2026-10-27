from io import StringIO

import pytest
from django.core.management import call_command

from {{ cookiecutter.project_slug }}.cms.models import HomePage

pytestmark = pytest.mark.django_db


def test_setup_cms_creates_missing_home_page():
    HomePage.objects.get().delete()
    out = StringIO()

    call_command("setup_cms", stdout=out)

    assert HomePage.objects.count() == 1
    assert "Created home page" in out.getvalue()


def test_setup_cms_keeps_existing_home_page():
    out = StringIO()

    call_command("setup_cms", stdout=out)

    assert HomePage.objects.count() == 1
    assert "already exists" in out.getvalue()
