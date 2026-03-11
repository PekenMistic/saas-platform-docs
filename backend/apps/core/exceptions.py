import logging
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    if isinstance(exc, PermissionDenied):
        return Response(
            {'detail': str(exc) or 'Permission denied.'},
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, Http404):
        return Response(
            {'detail': 'Not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    response = exception_handler(exc, context)

    if response is None:
        logger.exception('Unhandled exception in view', exc_info=exc)
        return Response(
            {'detail': 'Internal server error.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
