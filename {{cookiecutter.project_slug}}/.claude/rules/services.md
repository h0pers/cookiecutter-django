---
paths:
  - "{{ cookiecutter.project_slug }}/**/services.py"
  - "{{ cookiecutter.project_slug }}/**/exceptions.py"
---

# Services and app errors

- One `<Entity>Service` class per entity. Methods are `@staticmethod` or `@classmethod`; the class holds no state and is never instantiated.
- Keyword-only arguments (`def create(*, customer: User, total: Decimal) -> Order`) with type hints on every argument and return value.
- Database work only. Input arrives already validated by the view{% if cookiecutter.rest_api == 'DRF' %} or serializer{% endif %}: no `full_clean()`, no field checks, no `request`, no HTTP status codes{% if cookiecutter.rest_api == 'DRF' %}, no DRF imports{% endif %}.
- Wrap writes that touch more than one row or table in `@transaction.atomic`. Prefer `bulk_create` / `bulk_update` for many rows.
- Read methods return querysets with `select_related` / `prefetch_related` already applied for everything the callers render.
- Missing objects: `get_object_or_404(...)`, which raises Django's `Http404`.
- Raise an app error only for a rule that depends on database state. Never invent a rule the user didn't ask for.
- App errors live in the app's `exceptions.py`. `<App>Error(ApplicationError)` is the app's base; each rule subclasses it with the app prefix and passes a message plus `extra`:

  ```python
  from {{ cookiecutter.project_slug }}.core.exceptions import ApplicationError


  class OrdersError(ApplicationError):
      pass


  class OrdersClosedError(OrdersError):
      def __init__(self, *, order_id: int) -> None:
          super().__init__("This order is closed.", extra={"order_id": order_id})
  ```

- Every new service method gets a test in `tests/test_services.py`.
