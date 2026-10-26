{%- set run = 'docker compose -f docker-compose.local.yml run --rm django ' if cookiecutter.use_docker == 'y' else 'uv run ' -%}
{%- set slug = cookiecutter.project_slug -%}
---
name: add-endpoint
description: Add a DRF API endpoint the project's way - ModelSerializers with explicit fields, one generic view per URL (ListCreateAPIView / RetrieveUpdateDestroyAPIView) named *API that routes all database access through the app's service, drf-spectacular schema, URLs and API tests. Use when the user asks for a new endpoint or route, or to expose a model over the API.
argument-hint: "<app> <Entity>"
---

# Add an API endpoint

Arguments: `$ARGUMENTS` (app, then entity, e.g. `orders Order`). The service methods must exist; if not, run the `add-service` skill first. If the app has no `api/` package, create it as in the `new-app` skill.

All files below are in `{{ slug }}/<app>/api/`.

## 1. Serializers (`serializers.py`)

An output serializer for reads, and an input serializer for writes when the two differ:

```python
from rest_framework import serializers

from {{ slug }}.orders.models import Order


class OrderSerializer(serializers.ModelSerializer[Order]):
    class Meta:
        model = Order
        fields = [
            "id",
            "note",
            "is_closed",
            "created_at",
        ]


class OrderCreateSerializer(serializers.Serializer[Order]):
    note = serializers.CharField(max_length=200, required=False)
```

- Explicit `fields`, one per line; never `"__all__"`.
- Validation lives here: field arguments, `validate_<field>()`, `validate()`.

## 2. Views (`views.py`)

One generic view per URL, named after the generic with an `API` suffix:

```python
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema_view
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from {{ slug }}.orders.services import OrderService

from .serializers import OrderCreateSerializer
from .serializers import OrderSerializer


@extend_schema_view(
    get=extend_schema(summary="List your orders", tags=["orders"]),
    post=extend_schema(
        summary="Create an order", tags=["orders"], responses=OrderSerializer
    ),
)
class OrderListCreateAPI(ListCreateAPIView):
    def get_queryset(self):
        return OrderService.get_for_customer(customer=self.request.user)

    def get_serializer_class(self):
        return (
            OrderCreateSerializer if self.request.method == "POST" else OrderSerializer
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.create(customer=request.user, **serializer.validated_data)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
```

- `get_queryset()`, `create()`, `update()` and `perform_destroy()` call the service. Never `serializer.save()`, never the default `perform_create()` / `perform_update()`.
- Detail views (`RetrieveUpdateDestroyAPIView`) set `lookup_url_kwarg = "order_id"` and keep DRF's `get_object()`, which filters `get_queryset()` and checks object permissions.
- Permissions default to `IsAuthenticated` (`REST_FRAMEWORK` in `config/settings/base.py`); set `permission_classes` only to change that.
- App errors raised by services become `400 {"message": ..., "extra": {...}}` through `{{ slug }}.core.api.exception_handler`. Don't catch them in the view.

## 3. URLs (`urls.py`)

```python
from django.urls import path

from .views import OrderListCreateAPI

app_name = "orders"

urlpatterns = [
    path("", OrderListCreateAPI.as_view(), name="list-create"),
]
```

If the app isn't included yet, add `path("api/<app>/", include("{{ slug }}.<app>.api.urls", namespace="<app>")),` to the `# API URLS` block in `config/urls.py`.

## 4. Tests (`{{ slug }}/<app>/tests/test_api.py`)

```python
from http import HTTPStatus

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from {{ slug }}.orders.tests.factories import OrderFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user)
    return client


def test_list_returns_only_your_orders(api_client, user):
    OrderFactory.create(customer=user)
    OrderFactory.create()

    response = api_client.get(reverse("orders:list-create"))

    assert response.status_code == HTTPStatus.OK
    assert len(response.data) == 1


def test_create(api_client):
    response = api_client.post(reverse("orders:list-create"), {}, format="json")

    assert response.status_code == HTTPStatus.CREATED
```

Check status codes and response shapes, including app errors as `{"message": ..., "extra": {...}}`. Don't re-test service logic through the API.

## 5. Finish

`pre-commit run --all-files`, `{{ run }}mypy {{ slug }}`, `{{ run }}pytest {{ slug }}/<app>`. The schema is at `/api/schema/` and Swagger UI at `/api/docs/`.
