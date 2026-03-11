import logging
from django.core.management.base import BaseCommand, CommandError

from apps.tenants.models import Tenant
from apps.tenants.provisioner import TenantProvisioner

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Provision PostgreSQL schema for a specific tenant'

    def add_arguments(self, parser):
        parser.add_argument('tenant_id', type=str, help='UUID of the tenant to provision')

    def handle(self, *args, **options):
        tenant_id = options['tenant_id']

        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            raise CommandError(f'Tenant not found: {tenant_id}')

        self.stdout.write(f'Provisioning: {tenant.name} → {tenant.schema_name}')

        try:
            provisioner = TenantProvisioner(tenant)
            provisioner.provision()
            self.stdout.write(self.style.SUCCESS(f'Done. Schema {tenant.schema_name!r} is ready.'))
        except Exception as exc:
            logger.exception('Provisioning failed for tenant %s', tenant.slug)
            raise CommandError(f'Provisioning failed: {exc}') from exc
