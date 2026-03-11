from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.auth.serializers import TenantTokenObtainPairSerializer


class TenantLoginView(TokenObtainPairView):
    """Login endpoint — validates tenant context before issuing JWT."""
    serializer_class = TenantTokenObtainPairSerializer
    permission_classes = [AllowAny]


class TenantTokenRefreshView(TokenRefreshView):
    """Refresh JWT access token."""
    permission_classes = [AllowAny]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Blacklist the refresh token to log out."""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Return current user info."""
    user = request.user
    return Response({
        'id': str(user.pk),
        'email': getattr(user, 'email', ''),
        'full_name': getattr(user, 'full_name', ''),
        'role': getattr(user, 'role', ''),
    })
