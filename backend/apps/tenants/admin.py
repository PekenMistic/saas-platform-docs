from django.contrib import admin
from apps.tenants.models import Tenant, TenantDomain, BusinessType, ComponentRegistry


class TenantDomainInline(admin.TabularInline):
    model = TenantDomain
    extra = 1
    fields = ['domain', 'is_primary', 'is_custom', 'ssl_status']


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'business_type', 'plan_tier', 'status', 'created_at']
    list_filter = ['status', 'plan_tier', 'business_type']
    search_fields = ['name', 'slug']
    readonly_fields = ['id', 'schema_name', 'created_at', 'updated_at']
    inlines = [TenantDomainInline]


@admin.register(BusinessType)
class BusinessTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'version', 'is_active', 'created_at']
    list_filter = ['is_active', 'version']
    search_fields = ['code', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'tenant', 'is_primary', 'ssl_status']
    list_filter = ['ssl_status', 'is_primary']
    search_fields = ['domain']


@admin.register(ComponentRegistry)
class ComponentRegistryAdmin(admin.ModelAdmin):
    list_display = ['code', 'category', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['code']
