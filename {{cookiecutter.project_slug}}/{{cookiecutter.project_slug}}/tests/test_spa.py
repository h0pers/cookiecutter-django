from http import HTTPStatus

import pytest

pytestmark = pytest.mark.django_db


def test_spa_shell_serves_every_app_url(client):
    response = client.get("/app/some/vue/route/")

    assert response.status_code == HTTPStatus.OK
    assert b'<div id="app"></div>' in response.content
    # Tests run django-vite in dev mode, so the entry point is linked by its source path
    assert b"src/main.ts" in response.content
