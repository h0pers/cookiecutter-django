{%- set run = 'docker compose -f docker-compose.local.yml run --rm django ' if cookiecutter.use_docker == 'y' else 'uv run ' -%}
{%- set slug = cookiecutter.project_slug -%}
# AGENTS.md

Instructions for AI coding agents working in this repository. Human docs live in `README.md` and `docs/`.

## Stack

- Python 3.14, Django 6.0, PostgreSQL {{ cookiecutter.postgresql_version }}{% if cookiecutter.use_celery == 'y' %}, Redis and Celery (worker, beat, Flower){% endif %}
- `uv` for dependencies (`pyproject.toml` + `uv.lock`); ruff, djLint and mypy through pre-commit; pytest + pytest-django + factory_boy for tests
- django-allauth for accounts; custom user model in `{{ slug }}/users/` (`AUTH_USER_MODEL = "users.User"`, {{ cookiecutter.username_type }} login)
{%- if cookiecutter.rest_api == 'DRF' %}
- Django REST Framework + drf-spectacular; API under `/api/`, Swagger UI at `/api/docs/` (admin users only)
{%- elif cookiecutter.rest_api == 'Django Ninja' %}
- Django Ninja; API under `/api/`, routers mounted in `config/api.py`
{%- endif %}
{%- if cookiecutter.frontend_pipeline == 'Vite + Vue' %}
- Vue 3 + TypeScript + Vite in `frontend/`, served at `/app/` through django-vite; Tailwind 4 and shadcn-vue (`frontend/components.json`, skill in `.claude/skills/shadcn-vue`, MCP server in `.mcp.json`)
{%- endif %}
{%- if cookiecutter.use_wagtail == 'y' %}
- Wagtail 8 CMS: editor at `/cms/`, page models in `{{ slug }}/cms/`, and Wagtail serves `/` and every path not matched before it
{%- endif %}
{%- if cookiecutter.use_docker == 'y' %}
- Docker Compose for local (`docker-compose.local.yml`) and production (`docker-compose.production.yml`)
{%- endif %}

## Commands

Run from the project root.
{%- if cookiecutter.use_docker == 'y' %} Django runs in Docker: run `manage.py`, `pytest` and `mypy` in the `django` container, not on the host. The `justfile` has shortcuts (`just up`, `just pytest`, `just manage <command>`).
{%- endif %}

```bash
{%- if cookiecutter.use_docker == 'y' %}
docker compose -f docker-compose.local.yml up -d     # start the dev stack, Django at http://localhost:8000
{%- else %}
uv run python manage.py runserver                     # dev server at http://localhost:8000
{%- endif %}
{{ run }}pytest                                        # all tests
{{ run }}pytest {{ slug }}/users/tests/test_models.py  # one file
{{ run }}mypy {{ slug }}                               # type check
{{ run }}python manage.py makemigrations <app>        # after changing models
{{ run }}python manage.py makemigrations --check      # fails on model changes without a migration
pre-commit run --all-files                            # ruff, djLint and the other hooks
```

Add Python dependencies with `{{ run }}uv add <pkg>` (`--group dev` for tooling).
{%- if cookiecutter.frontend_pipeline == 'Vite + Vue' %}

Frontend, from `frontend/`: `npm run dev`, `npm run build` (type-checks, then builds), `npm run lint`, `npm run format`.
{%- endif %}

Before you finish a change, run pre-commit, mypy and the tests, plus `makemigrations --check` if you touched models.

## Layout

```
config/
├── settings/{base,local,test,production}.py   django-environ settings; local reads .envs/.local/
├── urls.py
{%- if cookiecutter.rest_api == 'DRF' %}
├── api_router.py                               DRF router mounted at /api/
{%- elif cookiecutter.rest_api == 'Django Ninja' %}
├── api.py                                      Ninja API mounted at /api/
{%- endif %}
{%- if cookiecutter.use_celery == 'y' %}
├── celery_app.py
{%- endif %}
{{ slug }}/
├── <app>/                     one Django app per domain
│   ├── models.py
│   ├── services.py            <Entity>Service: every database read and write
│   ├── exceptions.py          <App>Error and its subclasses
│   ├── admin.py
{%- if cookiecutter.rest_api != 'None' %}
│   ├── api/                   {% if cookiecutter.rest_api == 'DRF' %}serializers.py, views.py, urls.py{% else %}schema.py, views.py{% endif %}
{%- endif %}
{%- if cookiecutter.use_celery == 'y' %}
│   ├── tasks.py
{%- endif %}
│   ├── migrations/
│   └── tests/                 test_services.py, factories.py, ...
├── core/                      ApplicationError{% if cookiecutter.rest_api == 'DRF' %} and the API exception handler{% endif %}
├── users/                     custom User model{% if cookiecutter.use_wagtail == 'y' %}; wagtail_admin.py adapts Wagtail's user forms to it{% endif %}
{%- if cookiecutter.use_wagtail == 'y' %}
├── cms/                       Wagtail page models, HomePageService, setup_cms command
{%- endif %}
├── templates/                 Django templates{% if cookiecutter.frontend_pipeline == 'Vite + Vue' %}; spa.html is the Vue app shell{% endif %}
└── static/
{%- if cookiecutter.frontend_pipeline == 'Vite + Vue' %}
frontend/                      Vue app (src/, vite.config.ts, components.json)
{%- endif %}
{%- if cookiecutter.use_docker == 'y' %}
compose/                       Dockerfiles and start scripts for local and production
{%- endif %}
.envs/                         environment files: .local/ for development, .production/ for secrets
```

## Conventions

- **Views never touch the ORM.** Views{% if cookiecutter.rest_api == 'DRF' %}, serializers{% endif %} and forms validate input and shape output. `<Entity>Service` classes in `services.py` do every database read and write.
- **Services** are classes of `@staticmethod` / `@classmethod` methods with keyword-only arguments and type hints. They do database work only: no input validation, no `request`, no HTTP status codes. Wrap multi-step writes in `@transaction.atomic`. Read methods return querysets with `select_related` / `prefetch_related` already applied.
- **Errors:** `ApplicationError` (`{{ slug }}/core/exceptions.py`) → `<App>Error` in `<app>/exceptions.py` → `<App><Thing>Error`, e.g. `OrdersError` → `OrdersClosedError`. Raise them only for rules that depend on database state.{% if cookiecutter.rest_api == 'DRF' %} The API renders them as `400 {"message": ..., "extra": {...}}`.{% endif %}
{%- if cookiecutter.rest_api == 'DRF' %}
- **API (DRF):** for new endpoints, `ModelSerializer` with an explicit `fields` list (never `"__all__"`) and one generic view per URL, named after the generic with an `API` suffix (`OrderListCreateAPI`, `OrderRetrieveUpdateDestroyAPI`). Views call services from `get_queryset()`, `create()` and `update()`; never `serializer.save()`. The existing `UserViewSet` on the router predates this and stays as it is.
{%- endif %}
- **Users:** use `settings.AUTH_USER_MODEL` or `get_user_model()`, never `django.contrib.auth.models.User`.
- **Style:** pre-commit decides formatting (ruff with its default line length of 88; djLint for templates). Docstrings only when they explain something non-obvious. No `print`; use `logging`.

The `.claude/rules/` files hold the details for each area; the skills in `.claude/skills/` walk through adding an app, a service{% if cookiecutter.rest_api == 'DRF' %} or an endpoint{% endif %}.

## Gotchas

- `manage.py` defaults to `config.settings.local` and pytest to `config.settings.test` (`--ds` in `pyproject.toml`, with `--reuse-db`). Read settings with `env(...)` from django-environ and give a default unless production must set the value.
- A new app lives in `{{ slug }}/<app>/` with `name = "{{ slug }}.<app>"` in `apps.py`, and goes in `LOCAL_APPS` in `config/settings/base.py`.
- Tests that touch the database need `pytestmark = pytest.mark.django_db` or the `db` fixture. Build test data with factories (`<app>/tests/factories.py`); the `user` fixture is in `{{ slug }}/conftest.py`.
{%- if cookiecutter.use_celery == 'y' %}
- Celery runs tasks eagerly in local development (`CELERY_TASK_ALWAYS_EAGER` in `local.py`). Tests that run a task set it with the `settings` fixture, as in `users/tests/test_tasks.py`. Pass ids to tasks, not model instances.
{%- endif %}
{%- if cookiecutter.use_docker == 'y' %}
- Production `/start` runs `collectstatic` and gunicorn in every container; it doesn't migrate.{% if cookiecutter.deploy_ssh == 'y' %} One-off deploy steps (migrations, first superuser) go in `compose/production/django/release`, which runs once per deploy.{% else %} Run migrations as a separate step when you deploy.{% endif %}
{%- if cookiecutter.use_celery == 'y' %}
- On Colima, the Celery worker and beat reloaders can crash with `Too many open files (os error 24)` when other workloads use up inotify instances. Fix: `colima ssh -- sudo sysctl -w fs.inotify.max_user_instances=512`, and persist it in `/etc/sysctl.d/`.
{%- endif %}
{%- if cookiecutter.postgres_backup == 'WAL-G' %}
- Production backups use WAL-G (`compose/production/postgres/walg/`). Only run `walg-restore` when you're going to switch to the result; see the WAL-G backups guide.
{%- endif %}
{%- endif %}
{%- if cookiecutter.frontend_pipeline == 'Vite + Vue' %}
- Tailwind and shadcn-vue only load on `/app/`; the Django-rendered pages use Bootstrap. Tests run django-vite in dev mode, so they don't need a frontend build.
{%- endif %}
{%- if cookiecutter.use_wagtail == 'y' %}
- Wagtail's catch-all `path("", include(wagtail_urls))` must stay last in `config/urls.py`; add new routes above it.
- Wagtail pages are the exception to "views never touch the ORM": a page's `get_context()` may query the page tree (`self.get_children().live()`); anything else goes through a service. See `.claude/rules/wagtail.md`.
- A migration creates the HomePage and points the default Site at it. `{{ run }}python manage.py setup_cms` restores them on a database where they were deleted.
{%- endif %}

## Don't

- Edit migrations that are already committed; add a new one instead.
- Edit `.envs/.production/`, `uv.lock`{% if cookiecutter.frontend_pipeline == 'Vite + Vue' %} or `frontend/package-lock.json`{% endif %} by hand. A hook in `.claude/hooks/` blocks these edits.
- Put queries, `.save()` calls or business logic in views{% if cookiecutter.rest_api == 'DRF' %}, serializers{% endif %}, forms, model `save()` or signals.
- Commit secrets.
