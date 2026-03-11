from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.core.permissions import HasTenantContext


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasTenantContext])
def delta_sync_view(request):
    return Response({'synced': 0, 'conflicts': [], 'status': 'ok'}, status=status.HTTP_200_OK)


urlpatterns = [
    path('delta/', delta_sync_view, name='sync-delta'),
]
