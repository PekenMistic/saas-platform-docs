import logging
from django.db import connection
from django.utils import timezone

logger = logging.getLogger(__name__)


class TenantProvisioner:
    """
    Creates and tears down PostgreSQL schemas for tenants.

    Each tenant gets an isolated schema named after its schema_name field
    (typically tenant_{uuid_hex}). All tenant-specific tables live in this schema.
    """

    def __init__(self, tenant):
        self.tenant = tenant

    def provision(self) -> bool:
        """Create schema and run initial setup. Target: < 30 seconds."""
        schema = self.tenant.schema_name
        logger.info('Provisioning schema: %s for tenant: %s', schema, self.tenant.slug)

        with connection.cursor() as cursor:
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema}"')
            cursor.execute(f'SET search_path TO "{schema}", public')

        self._create_tenant_tables()
        self._seed_initial_data()

        logger.info('Provisioned schema: %s', schema)
        return True

    def _create_tenant_tables(self):
        """Create all required tables inside the tenant schema."""
        schema = self.tenant.schema_name
        with connection.cursor() as cursor:
            cursor.execute(f'SET search_path TO "{schema}", public')

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS branches (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    parent_branch_id UUID REFERENCES branches(id),
                    name VARCHAR(255) NOT NULL,
                    code VARCHAR(50) UNIQUE NOT NULL,
                    address TEXT,
                    phone VARCHAR(50),
                    timezone VARCHAR(100) DEFAULT 'Asia/Jakarta',
                    settings JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL DEFAULT 'cashier',
                    password_hash VARCHAR(255) NOT NULL,
                    pin_hash VARCHAR(255),
                    pin_expires_at TIMESTAMPTZ,
                    branch_id UUID REFERENCES branches(id),
                    is_active BOOLEAN DEFAULT true,
                    last_login_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_branch ON users(branch_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    device_id VARCHAR(255) NOT NULL,
                    device_type VARCHAR(50),
                    refresh_token_hash VARCHAR(255),
                    offline_token_hash VARCHAR(255),
                    offline_token_exp TIMESTAMPTZ,
                    ip_address INET,
                    last_active_at TIMESTAMPTZ DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS product_categories (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    sort_order INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT true
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    category_id UUID REFERENCES product_categories(id),
                    sku VARCHAR(100) UNIQUE,
                    barcode VARCHAR(100),
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    base_price NUMERIC(15,2) NOT NULL DEFAULT 0,
                    tax_rate NUMERIC(5,4) DEFAULT 0,
                    unit VARCHAR(50) DEFAULT 'pcs',
                    has_variants BOOLEAN DEFAULT false,
                    track_stock BOOLEAN DEFAULT true,
                    image_url VARCHAR(500),
                    metadata JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_updated ON products(updated_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_active ON products(is_active)')

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    product_id UUID NOT NULL REFERENCES products(id),
                    branch_id UUID NOT NULL REFERENCES branches(id),
                    quantity NUMERIC(15,4) DEFAULT 0,
                    reserved_quantity NUMERIC(15,4) DEFAULT 0,
                    min_quantity NUMERIC(15,4) DEFAULT 0,
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(product_id, branch_id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS shifts (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    branch_id UUID NOT NULL REFERENCES branches(id),
                    cashier_id UUID NOT NULL REFERENCES users(id),
                    opening_cash NUMERIC(15,2) DEFAULT 0,
                    closing_cash NUMERIC(15,2),
                    status VARCHAR(20) DEFAULT 'open',
                    opened_at TIMESTAMPTZ DEFAULT NOW(),
                    closed_at TIMESTAMPTZ,
                    notes TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    local_id VARCHAR(255) UNIQUE,
                    transaction_number VARCHAR(100) UNIQUE,
                    branch_id UUID NOT NULL REFERENCES branches(id),
                    cashier_id UUID REFERENCES users(id),
                    customer_id UUID,
                    shift_id UUID REFERENCES shifts(id),
                    status VARCHAR(50) DEFAULT 'completed',
                    subtotal NUMERIC(15,2) DEFAULT 0,
                    discount_amount NUMERIC(15,2) DEFAULT 0,
                    tax_amount NUMERIC(15,2) DEFAULT 0,
                    total_amount NUMERIC(15,2) NOT NULL,
                    payment_status VARCHAR(50) DEFAULT 'paid',
                    is_offline BOOLEAN DEFAULT false,
                    synced_at TIMESTAMPTZ,
                    conflict_data JSONB,
                    metadata JSONB DEFAULT '{}',
                    notes TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tx_branch ON transactions(branch_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tx_status ON transactions(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tx_created ON transactions(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tx_local_id ON transactions(local_id)')
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tx_branch_date
                ON transactions(branch_id, created_at DESC)
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transaction_items (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    transaction_id UUID NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
                    product_id UUID NOT NULL REFERENCES products(id),
                    product_name VARCHAR(255) NOT NULL,
                    quantity NUMERIC(15,4) NOT NULL,
                    unit_price NUMERIC(15,2) NOT NULL,
                    discount NUMERIC(15,2) DEFAULT 0,
                    subtotal NUMERIC(15,2) NOT NULL,
                    notes TEXT,
                    metadata JSONB DEFAULT '{}'
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    transaction_id UUID NOT NULL REFERENCES transactions(id),
                    method VARCHAR(50) NOT NULL,
                    amount NUMERIC(15,2) NOT NULL,
                    status VARCHAR(50) DEFAULT 'paid',
                    gateway VARCHAR(50),
                    gateway_tx_id VARCHAR(255),
                    gateway_response JSONB,
                    paid_at TIMESTAMPTZ,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_queue (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    device_id VARCHAR(255) NOT NULL,
                    branch_id UUID NOT NULL REFERENCES branches(id),
                    operation VARCHAR(20) NOT NULL,
                    entity_type VARCHAR(100) NOT NULL,
                    entity_id VARCHAR(255) NOT NULL,
                    payload JSONB NOT NULL,
                    checksum VARCHAR(255),
                    status VARCHAR(50) DEFAULT 'pending',
                    conflict_data JSONB,
                    retry_count INTEGER DEFAULT 0,
                    synced_at TIMESTAMPTZ,
                    created_at_device TIMESTAMPTZ NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)

            cursor.execute(f'SET search_path TO public')

    def _seed_initial_data(self):
        """Insert the default branch for a newly provisioned tenant."""
        schema = self.tenant.schema_name
        with connection.cursor() as cursor:
            cursor.execute(f'SET search_path TO "{schema}", public')
            cursor.execute("""
                INSERT INTO branches (name, code, timezone, is_active)
                VALUES (%s, %s, %s, true)
                ON CONFLICT (code) DO NOTHING
            """, [f'{self.tenant.name} - Main', 'MAIN', 'Asia/Jakarta'])
            cursor.execute('SET search_path TO public')

    def deprovision(self):
        """Soft-delete schema by renaming to _archived_. Does not DROP."""
        schema = self.tenant.schema_name
        archived = f'_archived_{schema}_{timezone.now().strftime("%Y%m%d")}'
        with connection.cursor() as cursor:
            cursor.execute(f'ALTER SCHEMA "{schema}" RENAME TO "{archived}"')
        logger.info('Deprovisioned schema: %s → %s', schema, archived)
