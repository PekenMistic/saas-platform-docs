import logging
from django.db import connection

logger = logging.getLogger(__name__)


class SchemaRouterMiddleware:
    """
    Sets PostgreSQL search_path to the tenant schema for every request.

    Must run AFTER TenantResolverMiddleware. If no tenant is set on the request,
    the search_path remains at the default (public schema only).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(request, 'tenant', None):
            self._set_search_path(request.tenant.schema_name)

        response = self.get_response(request)

        if getattr(request, 'tenant', None):
            self._reset_search_path()

        return response

    def _set_search_path(self, schema_name):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    'SET search_path TO %s, public',
                    [schema_name]
                )
            logger.debug('search_path set to: %s', schema_name)
        except Exception:
            logger.exception('Failed to set search_path to %s', schema_name)

    def _reset_search_path(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SET search_path TO public')
        except Exception:
            logger.exception('Failed to reset search_path')
