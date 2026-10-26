{%- set run = 'docker compose -f docker-compose.local.yml run --rm django ' if cookiecutter.use_docker == 'y' else 'uv run ' -%}
{%- set slug = cookiecutter.project_slug -%}
---
name: add-service
description: Add a model and/or service methods to an existing app the project's way - model with migration, an <Entity>Service class doing all database reads and writes, app errors, admin registration, a factory and service tests. Use when the user asks to store new data, add business logic, or add a read/write operation.
argument-hint: "<app> <Entity>"
---

# Add a model and its service

Arguments: `$ARGUMENTS` (app, then entity, e.g. `orders Order`). The app must exist; if not, run the `new-app` skill first.

Read the app's `models.py`, `services.py` and `exceptions.py` before changing them.

## 1. Model (skip if it exists)

In `{{ slug }}/<app>/models.py`:

```python
from django.conf import settings
from django.db import models


class Order(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    note = models.CharField(max_length=200, blank=True)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.pk}"
```

- `related_name` on every relation; `settings.AUTH_USER_MODEL` for user foreign keys.
- No logic in `save()` or signals.

Then `{{ run }}python manage.py makemigrations <app>`.

## 2. Service

In `{{ slug }}/<app>/services.py`, one class per entity:

```python
from django.db import transaction
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from {{ slug }}.orders.exceptions import OrdersClosedError
from {{ slug }}.orders.models import Order
from {{ slug }}.users.models import User


class OrderService:
    @staticmethod
    def get_for_customer(*, customer: User) -> QuerySet[Order]:
        return Order.objects.filter(customer=customer).select_related("customer")

    @staticmethod
    def get_by_id(*, order_id: int) -> Order:
        return get_object_or_404(Order.objects.select_related("customer"), pk=order_id)

    @staticmethod
    @transaction.atomic
    def create(*, customer: User, note: str = "") -> Order:
        return Order.objects.create(customer=customer, note=note)

    @staticmethod
    @transaction.atomic
    def close(*, order: Order) -> Order:
        if order.is_closed:
            raise OrdersClosedError(order_id=order.pk)
        order.is_closed = True
        order.save(update_fields=["is_closed"])
        return order
```

- `@staticmethod` / `@classmethod` only, keyword-only arguments, type hints.
- Database work only: no input validation, no `full_clean()`, no request or HTTP concepts.
- `@transaction.atomic` around writes; `bulk_create` for many rows; `select_related` / `prefetch_related` for what callers render.

## 3. App errors (only for real database-state rules)

If an operation must be refused because of what's in the database, and the user asked for that rule, add an error to `{{ slug }}/<app>/exceptions.py` and raise it from the service:

```python
class OrdersClosedError(OrdersError):
    def __init__(self, *, order_id: int) -> None:
        super().__init__("This order is closed.", extra={"order_id": order_id})
```

Name it `<App><Thing>Error` and subclass the app's `<App>Error`. Don't invent rules.

## 4. Admin

Register new models in `{{ slug }}/<app>/admin.py` with `@admin.register(Model)`; write `list_display` and similar lists one item per line.

## 5. Factory and tests

`{{ slug }}/<app>/tests/factories.py`, in the style of `users/tests/factories.py`:

```python
from factory import SubFactory
from factory.django import DjangoModelFactory

from {{ slug }}.orders.models import Order
from {{ slug }}.users.tests.factories import UserFactory


class OrderFactory(DjangoModelFactory[Order]):
    customer = SubFactory(UserFactory)

    class Meta:
        model = Order
```

`{{ slug }}/<app>/tests/test_services.py`:

```python
import pytest

from {{ slug }}.orders.exceptions import OrdersClosedError
from {{ slug }}.orders.services import OrderService
from {{ slug }}.orders.tests.factories import OrderFactory

pytestmark = pytest.mark.django_db


def test_close_marks_the_order_closed():
    order = OrderService.close(order=OrderFactory.create())

    assert order.is_closed


def test_close_refuses_a_closed_order():
    order = OrderFactory.create(is_closed=True)

    with pytest.raises(OrdersClosedError):
        OrderService.close(order=order)


def test_get_for_customer_loads_the_customer(django_assert_num_queries, user):
    OrderFactory.create(customer=user)

    with django_assert_num_queries(1):
        assert [
            order.customer for order in OrderService.get_for_customer(customer=user)
        ] == [user]
```

One test per service method, plus a query-count test for read methods.

## 6. Finish

`pre-commit run --all-files`, `{{ run }}mypy {{ slug }}`, `{{ run }}pytest {{ slug }}/<app>`, `{{ run }}python manage.py makemigrations --check`.{% if cookiecutter.rest_api == 'DRF' %} To expose the data over HTTP, continue with the `add-endpoint` skill.{% endif %}
