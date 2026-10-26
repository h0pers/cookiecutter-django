from http import HTTPStatus

from rest_framework.exceptions import NotFound

from {{ cookiecutter.project_slug }}.core.api import exception_handler
from {{ cookiecutter.project_slug }}.core.exceptions import ApplicationError


class OrdersClosedError(ApplicationError):
    pass


def test_application_error_is_a_400_with_message_and_extra():
    error = OrdersClosedError("This order is closed.", extra={"order_id": 1})

    response = exception_handler(error, {})

    assert response is not None
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.data == {
        "message": "This order is closed.",
        "extra": {"order_id": 1},
    }


def test_other_errors_keep_drf_handling():
    response = exception_handler(NotFound(), {})

    assert response is not None
    assert response.status_code == HTTPStatus.NOT_FOUND
