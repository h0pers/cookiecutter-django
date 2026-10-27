from http import HTTPStatus

import pytest
from django.urls import reverse

from {{ cookiecutter.project_slug }}.users.models import User

pytestmark = pytest.mark.django_db


def test_add_user(admin_client):
    url = reverse("wagtailusers_users:add")
    assert admin_client.get(url).status_code == HTTPStatus.OK

    response = admin_client.post(
        url,
        data={
            {%- if cookiecutter.username_type == "username" %}
            "username": "editor",
            {%- endif %}
            "email": "editor@example.com",
            "name": "Ed Itor",
            "password1": "My_R@ndom-P@ssw0rd",
            "password2": "My_R@ndom-P@ssw0rd",
        },
    )

    assert response.status_code == HTTPStatus.FOUND
    assert User.objects.get(email="editor@example.com").name == "Ed Itor"


def test_edit_user(admin_client, user: User):
    response = admin_client.get(reverse("wagtailusers_users:edit", args=[user.pk]))

    assert response.status_code == HTTPStatus.OK
