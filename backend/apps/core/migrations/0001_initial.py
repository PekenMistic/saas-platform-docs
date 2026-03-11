import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('tenant_id', models.UUIDField(db_index=True)),
                ('user_id', models.UUIDField(blank=True, null=True)),
                ('action', models.CharField(max_length=100)),
                ('entity_type', models.CharField(max_length=100)),
                ('entity_id', models.CharField(max_length=255)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('before_data', models.JSONField(blank=True, null=True)),
                ('after_data', models.JSONField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'audit_logs',
                'ordering': ['-created_at'],
            },
        ),
    ]
