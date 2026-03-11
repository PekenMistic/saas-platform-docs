from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
@permission_classes([AllowAny])
def midtrans_webhook_view(request):
    return Response({'detail': 'Invalid signature.'}, status=status.HTTP_400_BAD_REQUEST)


urlpatterns = [
    path('webhook/midtrans/', midtrans_webhook_view, name='payments-webhook-midtrans'),
]
