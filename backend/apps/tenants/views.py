from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsSaaSAdmin, HasTenantContext
from apps.tenants.models import Tenant, BusinessType
from apps.tenants.serializers import (
    TenantSerializer,
    TenantPublicSerializer,
    BusinessTypeSerializer,
)
from apps.tenants.provisioner import TenantProvisioner


class TenantListCreateView(generics.ListCreateAPIView):
    """List all tenants or create a new one (SaaS admin only)."""
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsSaaSAdmin]
    queryset = Tenant.objects.select_related('business_type').prefetch_related('domains')

    def perform_create(self, serializer):
        import uuid as uuid_lib
        uid = uuid_lib.uuid4()
        schema_name = f'tenant_{uid.hex}'
        tenant = serializer.save(id=uid, schema_name=schema_name)
        provisioner = TenantProvisioner(tenant)
        provisioner.provision()


class TenantDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a tenant (SaaS admin only)."""
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated, IsSaaSAdmin]
    queryset = Tenant.objects.select_related('business_type').prefetch_related('domains')


@api_view(['GET'])
@permission_classes([AllowAny])
def current_tenant_view(request):
    """Return public info for the current tenant (identified by domain)."""
    tenant = getattr(request, 'tenant', None)
    if not tenant:
        return Response({'detail': 'No tenant found for this domain.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = TenantPublicSerializer(tenant)
    return Response(serializer.data)


class BusinessTypeListView(generics.ListAPIView):
    """List all active business types."""
    serializer_class = BusinessTypeSerializer
    permission_classes = [AllowAny]
    queryset = BusinessType.objects.filter(is_active=True)
