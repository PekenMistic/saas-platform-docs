from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed


class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that validates users exist within the current tenant schema.

    The request object must have a valid tenant attached by TenantResolverMiddleware
    before this serializer is invoked.
    """

    def validate(self, attrs):
        request = self.context.get('request')
        tenant = getattr(request, 'tenant', None)

        if not tenant:
            raise AuthenticationFailed('Tenant context is required for authentication.')

        if not tenant.is_active:
            raise AuthenticationFailed('This tenant account is not active.')

        data = super().validate(attrs)

        data['tenant_id'] = str(tenant.id)
        data['tenant_slug'] = tenant.slug
        data['user_role'] = getattr(self.user, 'role', 'cashier')

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = getattr(user, 'role', 'cashier')
        token['tenant_id'] = str(getattr(user, 'tenant_id', ''))
        return token


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
