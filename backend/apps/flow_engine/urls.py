from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import HasTenantContext


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasTenantContext])
def flow_schema_view(request):
    tenant = request.tenant
    business_type = tenant.business_type
    return Response({
        'business_type': business_type.code,
        'version': business_type.version,
        'flow_schema': business_type.flow_schema,
        'ui_schema': business_type.ui_schema,
    })


urlpatterns = [
    path('schema/', flow_schema_view, name='flow-schema'),
]
