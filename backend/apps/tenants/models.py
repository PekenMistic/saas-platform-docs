import uuid
from django.db import models
from django.utils import timezone


class BusinessType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=100, blank=True)
    flow_schema = models.JSONField()
    ui_schema = models.JSONField(default=dict)
    default_settings = models.JSONField(default=dict)
    version = models.CharField(max_length=20, default='v1')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'business_types'
        ordering = ['code']

    def __str__(self):
        return f'{self.name} ({self.code})'


class Tenant(models.Model):
    PLAN_CHOICES = [
        ('starter', 'Starter'),
        ('professional', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]
    STATUS_CHOICES = [
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    schema_name = models.CharField(max_length=100, unique=True)
    business_type = models.ForeignKey(
        BusinessType,
        on_delete=models.PROTECT,
        related_name='tenants',
    )
    plan_tier = models.CharField(max_length=50, choices=PLAN_CHOICES, default='starter')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='trial')
    settings = models.JSONField(default=dict)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenants'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.slug})'

    @property
    def is_active(self):
        return self.status in ('active', 'trial')

    def get_setting(self, key: str, default=None):
        """Retrieve a setting using dot notation e.g. 'branding.primary_color'."""
        keys = key.split('.')
        val = self.settings
        for k in keys:
            if not isinstance(val, dict):
                return default
            val = val.get(k, default)
        return val


class TenantDomain(models.Model):
    SSL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='domains',
    )
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    is_primary = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)
    ssl_status = models.CharField(max_length=50, choices=SSL_STATUS_CHOICES, default='pending')
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tenant_domains'
        ordering = ['-is_primary', 'domain']

    def __str__(self):
        return f'{self.domain} → {self.tenant.slug}'


class ComponentRegistry(models.Model):
    CATEGORY_CHOICES = [
        ('input', 'Input'),
        ('display', 'Display'),
        ('action', 'Action'),
        ('navigation', 'Navigation'),
        ('layout', 'Layout'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    props_schema = models.JSONField()
    compatible_business_types = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'component_registry'
        ordering = ['category', 'code']

    def __str__(self):
        return f'{self.code} ({self.category})'
