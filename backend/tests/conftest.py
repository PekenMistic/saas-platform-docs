import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from apps.tenants.models import Tenant, TenantDomain, BusinessType


def create_full_tenant(name, slug, domain, business_type_code):
    bt, _ = BusinessType.objects.get_or_create(
        code=business_type_code,
        defaults={
            'name': business_type_code.replace('_', ' ').title(),
            'flow_schema': {'transaction_flow': []},
            'ui_schema': {},
            'default_settings': {},
        },
    )
    import uuid as uuid_lib
    uid = uuid_lib.uuid4()
    tenant = Tenant.objects.create(
        id=uid,
        name=name,
        slug=slug,
        schema_name=f'tenant_{uid.hex}',
        business_type=bt,
        status='active',
    )
    TenantDomain.objects.create(tenant=tenant, domain=domain, is_primary=True)
    return tenant


@pytest.fixture
def tenant_a(db):
    return create_full_tenant(
        name='Kedai Kopi A',
        slug='kedai-kopi-a',
        domain='shop-a.example.com',
        business_type_code='coffee_shop',
    )


@pytest.fixture
def tenant_b(db):
    return create_full_tenant(
        name='Laundry B',
        slug='laundry-b',
        domain='laundry-b.example.com',
        business_type_code='laundry',
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client_a(api_client, tenant_a):
    api_client.credentials(HTTP_HOST='shop-a.example.com')
    return api_client
