from rest_framework import serializers
from apps.tenants.models import Tenant, TenantDomain, BusinessType


class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'code', 'name', 'icon', 'version', 'is_active']


class TenantDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantDomain
        fields = ['id', 'domain', 'is_primary', 'is_custom', 'ssl_status', 'verified_at']


class TenantSerializer(serializers.ModelSerializer):
    business_type = BusinessTypeSerializer(read_only=True)
    business_type_id = serializers.PrimaryKeyRelatedField(
        queryset=BusinessType.objects.all(),
        source='business_type',
        write_only=True,
    )
    domains = TenantDomainSerializer(many=True, read_only=True)

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'slug', 'schema_name',
            'business_type', 'business_type_id',
            'plan_tier', 'status', 'settings',
            'trial_ends_at', 'created_at', 'updated_at',
            'domains',
        ]
        read_only_fields = ['id', 'schema_name', 'created_at', 'updated_at']


class TenantPublicSerializer(serializers.ModelSerializer):
    """Minimal tenant info exposed to frontend for branding."""
    business_type_code = serializers.CharField(source='business_type.code', read_only=True)

    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'business_type_code', 'plan_tier', 'status', 'settings']
