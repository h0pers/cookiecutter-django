{%- set run = 'docker compose -f docker-compose.local.yml run --rm django ' if cookiecutter.use_docker == 'y' else 'uv run ' -%}
{%- set slug = cookiecutter.project_slug -%}
---
name: new-app
description: Create a new Django app in {{ slug }}/ with this project's layout (models, services, exceptions, admin, tests{% if cookiecutter.rest_api == 'DRF' %}, api{% endif %}) and register it. Use when the user asks for a new app, a new domain, or models that don't belong to an existing app.
argument-hint: "<app_name>"
---

# Create a new Django app

App name: `$ARGUMENTS` (lowercase, plural noun, e.g. `orders`). Below, `<app>` is the app name and `<App>` its CamelCase form (`Orders`).

## 1. Check first

`{{ slug }}/<app>/` must not exist. If the models belong to an existing app, extend that app instead and stop here.

## 2. Create the app package

```
{{ slug }}/<app>/
├── __init__.py              empty
├── apps.py
├── exceptions.py
├── models.py
├── services.py              empty
├── admin.py
├── migrations/__init__.py   empty
└── tests/
    ├── __init__.py          empty
    └── factories.py         empty
```

`apps.py`:

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class <App>Config(AppConfig):
    name = "{{ slug }}.<app>"
    verbose_name = _("<App>")
```

`exceptions.py`:

```python
from {{ slug }}.core.exceptions import ApplicationError


class <App>Error(ApplicationError):
    pass
```

`models.py` starts with `from django.db import models` and `admin.py` with `from django.contrib import admin`. Fill them, and `services.py`, with the `add-service` skill.
{%- if cookiecutter.rest_api == 'DRF' %}

## 3. API package

```
{{ slug }}/<app>/api/
├── __init__.py          empty
├── serializers.py       empty
├── views.py             empty
└── urls.py
```

`api/urls.py`:

```python
app_name = "<app>"

urlpatterns = []
```

Include it in `config/urls.py`, in the `# API URLS` list:

```python
urlpatterns += [
    # ...
    path("api/<app>/", include("{{ slug }}.<app>.api.urls", namespace="<app>")),
]
```

Add endpoints with the `add-endpoint` skill.
{%- endif %}

## {% if cookiecutter.rest_api == 'DRF' %}4{% else %}3{% endif %}. Register the app

Add `"{{ slug }}.<app>",` to `LOCAL_APPS` in `config/settings/base.py`, under `# Your stuff: custom apps go here`.

## {% if cookiecutter.rest_api == 'DRF' %}5{% else %}4{% endif %}. Finish

1. If you added models: `{{ run }}python manage.py makemigrations <app>`, then `{{ run }}python manage.py makemigrations --check`.
2. `pre-commit run --all-files`, `{{ run }}mypy {{ slug }}`, `{{ run }}pytest`.
3. Tell the user which files you created and what comes next (models and services{% if cookiecutter.rest_api == 'DRF' %}, then endpoints{% endif %}).
