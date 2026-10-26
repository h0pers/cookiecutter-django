from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from {{ cookiecutter.project_slug }}.core.exceptions import ApplicationError


def exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    # Errors services raise on purpose are client errors with one shape;
    # DRF's own errors keep its handling
    if isinstance(exc, ApplicationError):
        return Response(
            {"message": exc.message, "extra": exc.extra},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return drf_exception_handler(exc, context)
