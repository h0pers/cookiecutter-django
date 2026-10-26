---
paths:
  - "{{ cookiecutter.project_slug }}/**/tests/**"
  - "{{ cookiecutter.project_slug }}/conftest.py"
---

# Tests

- pytest + pytest-django, function-style tests (`def test_...`) with plain `assert`. No `unittest.TestCase` classes.
- Files mirror the code: `test_services.py` for services{% if cookiecutter.rest_api != 'None' %}, `test_api.py` for endpoints{% endif %}, `test_<module>.py` otherwise.
- Tests that touch the database: `pytestmark = pytest.mark.django_db` at the top of the module, or the `db` fixture.
- Build test data with factory_boy factories in `<app>/tests/factories.py` (see `users/tests/factories.py`); the `user` fixture lives in `{{ cookiecutter.project_slug }}/conftest.py`. Use services for data that needs business rules.
- Service tests are the main tests: call the service and assert on the database or the returned objects.
- Read methods: assert the query count with the `django_assert_num_queries` fixture, so N+1 regressions fail.
{%- if cookiecutter.rest_api == 'DRF' %}
- API tests: `rest_framework.test.APIClient`, `reverse(...)`, `format="json"` for bodies. Check status codes and response shapes, including the app error shape `{"message": ..., "extra": {...}}`. Don't re-test service logic through the API.
{%- endif %}
- Compare status codes with `http.HTTPStatus` (`HTTPStatus.OK`), not bare numbers; ruff flags magic values.
