import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='BusinessType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('icon', models.CharField(blank=True, max_length=100)),
                ('flow_schema', models.JSONField()),
                ('ui_schema', models.JSONField(default=dict)),
                ('default_settings', models.JSONField(default=dict)),
                ('version', models.CharField(default='v1', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'business_types',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('schema_name', models.CharField(max_length=100, unique=True)),
                ('business_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tenants', to='tenants.businesstype')),
                ('plan_tier', models.CharField(
                    choices=[('starter', 'Starter'), ('professional', 'Professional'), ('enterprise', 'Enterprise')],
                    default='starter', max_length=50,
                )),
                ('status', models.CharField(
                    choices=[('trial', 'Trial'), ('active', 'Active'), ('suspended', 'Suspended'), ('cancelled', 'Cancelled')],
                    default='trial', max_length=50,
                )),
                ('settings', models.JSONField(default=dict)),
                ('trial_ends_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'tenants',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TenantDomain',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='domains', to='tenants.tenant')),
                ('domain', models.CharField(db_index=True, max_length=255, unique=True)),
                ('is_primary', models.BooleanField(default=False)),
                ('is_custom', models.BooleanField(default=False)),
                ('ssl_status', models.CharField(
                    choices=[('pending', 'Pending'), ('active', 'Active'), ('failed', 'Failed')],
                    default='pending', max_length=50,
                )),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tenant_domains',
                'ordering': ['-is_primary', 'domain'],
            },
        ),
        migrations.CreateModel(
            name='ComponentRegistry',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=100, unique=True)),
                ('category', models.CharField(
                    choices=[('input', 'Input'), ('display', 'Display'), ('action', 'Action'), ('navigation', 'Navigation'), ('layout', 'Layout')],
                    max_length=50,
                )),
                ('props_schema', models.JSONField()),
                ('compatible_business_types', models.JSONField(default=list)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'component_registry',
                'ordering': ['category', 'code'],
            },
        ),
    ]
