---
paths:
  - "{{ cookiecutter.project_slug }}/**/api/**"
  - "config/api_router.py"
  - "config/urls.py"
---

# API layer (DRF)

- An app's `api/` holds `serializers.py`, `views.py` and `urls.py`. Nothing in `api/` queries the ORM: views call the app's service.
- `ModelSerializer` with an explicit `fields` list, one field per line, never `"__all__"`. Input fields that aren't model fields are declared on the serializer with their own validation.
- Validation happens in the serializer: `min_length`, `max_length`, `validate_<field>()`, `validate()`.
- One DRF generic view per URL: `ListCreateAPIView` for `orders/`, `RetrieveUpdateDestroyAPIView` for `orders/<id>/`. Name it after the generic with the entity prefix and an `API` suffix (`OrderListCreateAPI`, `OrderRetrieveUpdateDestroyAPI`).
- Route every database access through the service by overriding:
  - `get_queryset()` → the service's read method. Detail views set `lookup_url_kwarg` and let DRF's `get_object()` filter that queryset and check object permissions.
  - `create()` / `update()` → `serializer.is_valid(raise_exception=True)`, the service with `**serializer.validated_data`, then the output serializer.
  - `perform_destroy()` → the service's delete method.
- Never call `serializer.save()` or rely on the default `perform_create()` / `perform_update()`.
- `get_serializer_class()` returns the input serializer for writes and the output serializer for reads.
- Document endpoints for drf-spectacular with `@extend_schema` / `@extend_schema_view` (summary, tags, and `responses` when the output serializer differs from the input one).
- Register the app's URLs in `<app>/api/urls.py` (`app_name = "<app>"`) and include it in `config/urls.py` under `api/`. The existing `UserViewSet` on `config/api_router.py` stays as it is.
- Errors: raise app errors in services; `{{ cookiecutter.project_slug }}.core.api.exception_handler` renders them as `400 {"message": ..., "extra": {...}}`. Don't build error responses by hand.
- Every endpoint gets tests in `tests/test_api.py`. Use the `add-endpoint` skill for a new endpoint.
