import logging
from django.core.management.base import BaseCommand
from django.db import connection

from apps.tenants.models import Tenant
from apps.tenants.provisioner import TenantProvisioner

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run provisioner for all active/trial tenant schemas to apply table changes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            nargs='+',
            default=['active', 'trial'],
            help='Tenant status filter (default: active trial)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='List tenants that would be migrated without running',
        )

    def handle(self, *args, **options):
        statuses = options['status']
        dry_run = options['dry_run']

        tenants = Tenant.objects.filter(status__in=statuses).order_by('created_at')
        total = tenants.count()

        if total == 0:
            self.stdout.write('No tenants found matching the given status filter.')
            return

        self.stdout.write(f'Found {total} tenant(s) to migrate (statuses: {statuses})')

        if dry_run:
            for tenant in tenants:
                self.stdout.write(f'  [DRY-RUN] {tenant.name} → {tenant.schema_name}')
            return

        success = 0
        failed = 0

        for tenant in tenants:
            try:
                provisioner = TenantProvisioner(tenant)
                provisioner._create_tenant_tables()
                success += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Migrated: {tenant.name} ({tenant.schema_name})'))
            except Exception as exc:
                failed += 1
                self.stderr.write(self.style.ERROR(f'  ✗ Failed: {tenant.name} — {exc}'))
                logger.exception('Failed to migrate tenant %s', tenant.slug)

        with connection.cursor() as cursor:
            cursor.execute('SET search_path TO public')

        self.stdout.write(
            self.style.SUCCESS(f'\nDone. {success} migrated, {failed} failed.')
        )
