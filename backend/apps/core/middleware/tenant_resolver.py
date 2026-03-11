import logging
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)

BYPASS_PATHS = ('/health/', '/admin/', '/api/schema/', '/api/docs/')


class TenantResolverMiddleware:
    """
    Resolves the current tenant from the request domain.

    Reads the domain from (in priority order):
    1. X-Tenant-Domain header (injected by Cloudflare/Next.js middleware)
    2. X-Forwarded-Host header
    3. HTTP_HOST

    Sets request.tenant to the Tenant instance, or None for bypassed paths.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.tenant = None

        if self._should_bypass(request):
            return self.get_response(request)

        domain = self._extract_domain(request)
        if domain:
            request.tenant = self._resolve_tenant(domain)

        return self.get_response(request)

    def _should_bypass(self, request):
        path = request.path_info
        return any(path.startswith(p) for p in BYPASS_PATHS)

    def _extract_domain(self, request):
        domain = (
            request.META.get('HTTP_X_TENANT_DOMAIN')
            or request.META.get('HTTP_X_FORWARDED_HOST')
            or request.META.get('HTTP_HOST', '')
        )
        return domain.split(':')[0].lower().strip() if domain else None

    def _resolve_tenant(self, domain):
        cache_key = f'tenant:domain:{domain}'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            from apps.tenants.models import TenantDomain
            tenant_domain = (
                TenantDomain.objects
                .select_related('tenant', 'tenant__business_type')
                .get(domain=domain)
            )
            tenant = tenant_domain.tenant
            from django.conf import settings
            ttl = getattr(settings, 'TENANT_CACHE_TTL_SECONDS', 300)
            cache.set(cache_key, tenant, ttl)
            return tenant
        except Exception:
            logger.debug('No tenant found for domain: %s', domain)
            return None
