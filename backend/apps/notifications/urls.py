from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import HasTenantContext


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasTenantContext])
def notification_list_view(request):
    return Response({'results': [], 'count': 0})


urlpatterns = [
    path('', notification_list_view, name='notification-list'),
]
