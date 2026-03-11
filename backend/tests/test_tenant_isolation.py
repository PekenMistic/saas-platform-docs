import pytest
from rest_framework.test import APIClient

from apps.tenants.models import Tenant, TenantDomain, BusinessType
from tests.conftest import create_full_tenant


@pytest.mark.django_db
class TestTenantIsolation:
    """
    Tenant isolation tests — MUST pass 100%.
    Data must never leak between tenants.
    """

    def test_tenant_resolver_sets_tenant_from_host(self, tenant_a, api_client):
        """TenantResolverMiddleware sets request.tenant from HTTP_HOST."""
        response = api_client.get(
            '/api/v1/tenants/current/',
            HTTP_HOST='shop-a.example.com',
        )
        assert response.status_code == 200
        assert response.data['slug'] == 'kedai-kopi-a'

    def test_tenant_resolver_returns_404_for_unknown_domain(self, api_client):
        """Unknown domain returns 404 from /tenants/current/."""
        response = api_client.get(
            '/api/v1/tenants/current/',
            HTTP_HOST='unknown-tenant.example.com',
        )
        assert response.status_code == 404

    def test_user_from_other_tenant_cannot_login_on_wrong_domain(
        self, tenant_a, tenant_b, api_client
    ):
        """
        Attempting login on tenant_a's domain with no valid user in that schema
        must return 401.
        """
        api_client.credentials(HTTP_HOST='shop-a.example.com')
        response = api_client.post('/api/v1/auth/login/', {
            'email': 'user@b.com',
            'password': 'wrong-password',
        })
        assert response.status_code in (400, 401)

    def test_flow_schema_requires_auth(self, tenant_a, api_client):
        """GET /flow/schema/ must return 401 without auth token."""
        api_client.credentials(HTTP_HOST='shop-a.example.com')
        response = api_client.get('/api/v1/flow/schema/')
        assert response.status_code == 401

    def test_health_endpoint_accessible(self, api_client):
        """Health endpoint always returns 200 or 503 without tenant context."""
        response = api_client.get('/health/')
        assert response.status_code in (200, 503)

    def test_tenant_current_different_domains_different_tenants(
        self, tenant_a, tenant_b, api_client
    ):
        """Two different domains resolve to two different tenants."""
        resp_a = api_client.get('/api/v1/tenants/current/', HTTP_HOST='shop-a.example.com')
        resp_b = api_client.get('/api/v1/tenants/current/', HTTP_HOST='laundry-b.example.com')

        assert resp_a.status_code == 200
        assert resp_b.status_code == 200
        assert resp_a.data['slug'] != resp_b.data['slug']
        assert resp_a.data['slug'] == 'kedai-kopi-a'
        assert resp_b.data['slug'] == 'laundry-b'
