from django.core.management.base import BaseCommand
from apps.tenants.models import BusinessType

BUSINESS_TYPES = [
    {
        'code': 'coffee_shop',
        'name': 'Coffee Shop / Kafe',
        'icon': 'coffee',
        'version': 'v1',
        'flow_schema': {
            'transaction_flow': [
                {
                    'key': 'select_products',
                    'label': 'Pilih Menu',
                    'component': 'product_grid',
                    'can_go_back': False,
                    'on_complete': 'emit:products_selected',
                    'props': {'category_filter': True, 'show_stock': False},
                },
                {
                    'key': 'customize_order',
                    'label': 'Kustomisasi',
                    'component': 'order_modifier',
                    'can_go_back': True,
                    'on_complete': 'emit:order_customized',
                    'props': {'modifiers': ['temperature', 'sugar_level', 'size']},
                },
                {
                    'key': 'cart_review',
                    'label': 'Keranjang',
                    'component': 'cart_summary',
                    'can_go_back': True,
                    'on_complete': 'emit:cart_confirmed',
                    'props': {'show_discount': True},
                },
                {
                    'key': 'payment',
                    'label': 'Pembayaran',
                    'component': 'payment_method',
                    'can_go_back': True,
                    'on_complete': 'emit:payment_completed',
                    'props': {'methods': ['cash', 'qris', 'debit']},
                },
                {
                    'key': 'receipt',
                    'label': 'Struk',
                    'component': 'receipt_display',
                    'can_go_back': False,
                    'on_complete': 'emit:receipt_done',
                    'props': {'print_enabled': True, 'show_qr': True},
                },
            ]
        },
        'ui_schema': {
            'theme': 'coffee',
            'primary_color': '#4E342E',
            'layout': 'split_screen',
        },
        'default_settings': {
            'branding': {'primary_color': '#4E342E', 'app_name': 'POS Kafe'},
            'features': {'loyalty_points': True, 'kitchen_display': True},
            'regional': {'timezone': 'Asia/Jakarta', 'currency': 'IDR', 'locale': 'id-ID'},
        },
    },
    {
        'code': 'laundry',
        'name': 'Laundry',
        'icon': 'shirt',
        'version': 'v1',
        'flow_schema': {
            'transaction_flow': [
                {
                    'key': 'customer_intake',
                    'label': 'Data Pelanggan',
                    'component': 'customer_form',
                    'can_go_back': False,
                    'on_complete': 'emit:customer_entered',
                    'props': {'require_phone': True},
                },
                {
                    'key': 'select_services',
                    'label': 'Pilih Layanan',
                    'component': 'service_selector',
                    'can_go_back': True,
                    'on_complete': 'emit:services_selected',
                    'props': {'weight_input': True},
                },
                {
                    'key': 'cart_review',
                    'label': 'Ringkasan',
                    'component': 'cart_summary',
                    'can_go_back': True,
                    'on_complete': 'emit:cart_confirmed',
                    'props': {'show_pickup_date': True},
                },
                {
                    'key': 'payment',
                    'label': 'Pembayaran',
                    'component': 'payment_method',
                    'can_go_back': True,
                    'on_complete': 'emit:payment_completed',
                    'props': {'methods': ['cash', 'qris', 'debit'], 'allow_partial': True},
                },
                {
                    'key': 'receipt',
                    'label': 'Nota',
                    'component': 'receipt_display',
                    'can_go_back': False,
                    'on_complete': 'emit:receipt_done',
                    'props': {'print_enabled': True, 'show_pickup_date': True},
                },
            ]
        },
        'ui_schema': {'theme': 'laundry', 'layout': 'single_column'},
        'default_settings': {
            'branding': {'primary_color': '#1565C0', 'app_name': 'POS Laundry'},
            'features': {'loyalty_points': False, 'pickup_reminder': True},
            'regional': {'timezone': 'Asia/Jakarta', 'currency': 'IDR', 'locale': 'id-ID'},
        },
    },
    {
        'code': 'vehicle_dealer',
        'name': 'Dealer Kendaraan',
        'icon': 'car',
        'version': 'v1',
        'flow_schema': {
            'transaction_flow': [
                {'key': 'select_vehicle', 'label': 'Pilih Kendaraan', 'component': 'product_grid', 'can_go_back': False, 'on_complete': 'emit:vehicle_selected', 'props': {}},
                {'key': 'customer_data', 'label': 'Data Pembeli', 'component': 'customer_form', 'can_go_back': True, 'on_complete': 'emit:customer_entered', 'props': {'require_ktp': True}},
                {'key': 'financing', 'label': 'Pembiayaan', 'component': 'financing_selector', 'can_go_back': True, 'on_complete': 'emit:financing_selected', 'props': {}},
                {'key': 'trade_in', 'label': 'Tukar Tambah', 'component': 'trade_in_form', 'can_go_back': True, 'on_complete': 'emit:trade_in_done', 'props': {'optional': True}},
                {'key': 'cart_review', 'label': 'Ringkasan', 'component': 'cart_summary', 'can_go_back': True, 'on_complete': 'emit:cart_confirmed', 'props': {}},
                {'key': 'payment', 'label': 'Pembayaran DP', 'component': 'payment_method', 'can_go_back': True, 'on_complete': 'emit:payment_completed', 'props': {'methods': ['cash', 'transfer', 'financing']}},
                {'key': 'bast', 'label': 'BAST', 'component': 'document_generator', 'can_go_back': False, 'on_complete': 'emit:bast_done', 'props': {'template': 'bast_vehicle'}},
            ]
        },
        'ui_schema': {'theme': 'automotive', 'layout': 'wizard'},
        'default_settings': {
            'branding': {'primary_color': '#263238', 'app_name': 'Dealer POS'},
            'features': {'bpjs_integration': False, 'financing': True},
            'regional': {'timezone': 'Asia/Jakarta', 'currency': 'IDR', 'locale': 'id-ID'},
        },
    },
    {
        'code': 'clinic',
        'name': 'Klinik / Apotek',
        'icon': 'stethoscope',
        'version': 'v1',
        'flow_schema': {
            'transaction_flow': [
                {'key': 'patient_registration', 'label': 'Registrasi Pasien', 'component': 'patient_form', 'can_go_back': False, 'on_complete': 'emit:patient_registered', 'props': {'require_nik': True}},
                {'key': 'soap_note', 'label': 'SOAP', 'component': 'soap_form', 'can_go_back': True, 'on_complete': 'emit:soap_done', 'props': {}},
                {'key': 'prescription', 'label': 'Resep', 'component': 'product_grid', 'can_go_back': True, 'on_complete': 'emit:prescription_done', 'props': {'category': 'medicine'}},
                {'key': 'bpjs_verification', 'label': 'BPJS', 'component': 'bpjs_checker', 'can_go_back': True, 'on_complete': 'emit:bpjs_done', 'props': {'optional': True}},
                {'key': 'payment', 'label': 'Pembayaran', 'component': 'payment_method', 'can_go_back': True, 'on_complete': 'emit:payment_completed', 'props': {'methods': ['cash', 'bpjs', 'qris']}},
                {'key': 'receipt', 'label': 'Bukti', 'component': 'receipt_display', 'can_go_back': False, 'on_complete': 'emit:receipt_done', 'props': {'include_prescription': True}},
            ]
        },
        'ui_schema': {'theme': 'medical', 'layout': 'tabbed'},
        'default_settings': {
            'branding': {'primary_color': '#00695C', 'app_name': 'Klinik POS'},
            'features': {'bpjs_integration': True, 'emr': True},
            'regional': {'timezone': 'Asia/Jakarta', 'currency': 'IDR', 'locale': 'id-ID'},
        },
    },
    {
        'code': 'retail_store',
        'name': 'Toko Retail',
        'icon': 'shopping_bag',
        'version': 'v1',
        'flow_schema': {
            'transaction_flow': [
                {'key': 'scan_products', 'label': 'Scan Produk', 'component': 'barcode_scanner', 'can_go_back': False, 'on_complete': 'emit:scan_done', 'props': {'manual_input': True}},
                {'key': 'cart_review', 'label': 'Keranjang', 'component': 'cart_summary', 'can_go_back': True, 'on_complete': 'emit:cart_confirmed', 'props': {'show_discount': True}},
                {'key': 'payment', 'label': 'Pembayaran', 'component': 'payment_method', 'can_go_back': True, 'on_complete': 'emit:payment_completed', 'props': {'methods': ['cash', 'qris', 'debit', 'midtrans']}},
                {'key': 'receipt', 'label': 'Struk', 'component': 'receipt_display', 'can_go_back': False, 'on_complete': 'emit:receipt_done', 'props': {'print_enabled': True}},
            ]
        },
        'ui_schema': {'theme': 'retail', 'layout': 'split_screen'},
        'default_settings': {
            'branding': {'primary_color': '#E65100', 'app_name': 'Toko POS'},
            'features': {'loyalty_points': True, 'stock_alert': True},
            'regional': {'timezone': 'Asia/Jakarta', 'currency': 'IDR', 'locale': 'id-ID'},
        },
    },
    {
        'code': 'salon_barbershop',
        'name': 'Salon / Barbershop',
        'icon': 'scissors',
        'version': 'v1',
        'flow_schema': {
            'transaction_flow': [
                {'key': 'select_stylist', 'label': 'Pilih Stylist', 'component': 'staff_selector', 'can_go_back': False, 'on_complete': 'emit:stylist_selected', 'props': {}},
                {'key': 'select_services', 'label': 'Pilih Layanan', 'component': 'service_selector', 'can_go_back': True, 'on_complete': 'emit:services_selected', 'props': {}},
                {'key': 'cart_review', 'label': 'Ringkasan', 'component': 'cart_summary', 'can_go_back': True, 'on_complete': 'emit:cart_confirmed', 'props': {'show_commission': True}},
                {'key': 'payment', 'label': 'Pembayaran', 'component': 'payment_method', 'can_go_back': True, 'on_complete': 'emit:payment_completed', 'props': {'methods': ['cash', 'qris', 'debit']}},
                {'key': 'receipt', 'label': 'Struk', 'component': 'receipt_display', 'can_go_back': False, 'on_complete': 'emit:receipt_done', 'props': {}},
            ]
        },
        'ui_schema': {'theme': 'salon', 'layout': 'single_column'},
        'default_settings': {
            'branding': {'primary_color': '#880E4F', 'app_name': 'Salon POS'},
            'features': {'commission_tracking': True, 'booking': True},
            'regional': {'timezone': 'Asia/Jakarta', 'currency': 'IDR', 'locale': 'id-ID'},
        },
    },
    {
        'code': 'hotel_guesthouse',
        'name': 'Hotel / Penginapan',
        'icon': 'bed',
        'version': 'v1',
        'flow_schema': {
            'transaction_flow': [
                {'key': 'check_availability', 'label': 'Cek Kamar', 'component': 'room_grid', 'can_go_back': False, 'on_complete': 'emit:room_selected', 'props': {}},
                {'key': 'guest_data', 'label': 'Data Tamu', 'component': 'guest_form', 'can_go_back': True, 'on_complete': 'emit:guest_entered', 'props': {'require_id': True}},
                {'key': 'cart_review', 'label': 'Ringkasan', 'component': 'cart_summary', 'can_go_back': True, 'on_complete': 'emit:cart_confirmed', 'props': {'show_dates': True}},
                {'key': 'payment', 'label': 'Pembayaran', 'component': 'payment_method', 'can_go_back': True, 'on_complete': 'emit:payment_completed', 'props': {'methods': ['cash', 'transfer', 'qris', 'midtrans']}},
                {'key': 'receipt', 'label': 'Bukti Check-in', 'component': 'receipt_display', 'can_go_back': False, 'on_complete': 'emit:receipt_done', 'props': {'include_key': True}},
            ]
        },
        'ui_schema': {'theme': 'hospitality', 'layout': 'grid'},
        'default_settings': {
            'branding': {'primary_color': '#1A237E', 'app_name': 'Hotel POS'},
            'features': {'room_management': True, 'housekeeping': True},
            'regional': {'timezone': 'Asia/Jakarta', 'currency': 'IDR', 'locale': 'id-ID'},
        },
    },
    {
        'code': 'restaurant',
        'name': 'Restoran',
        'icon': 'utensils',
        'version': 'v1',
        'flow_schema': {
            'transaction_flow': [
                {'key': 'select_table', 'label': 'Pilih Meja', 'component': 'table_map', 'can_go_back': False, 'on_complete': 'emit:table_selected', 'props': {}},
                {'key': 'select_products', 'label': 'Pesan Menu', 'component': 'product_grid', 'can_go_back': True, 'on_complete': 'emit:products_selected', 'props': {'send_to_kitchen': True}},
                {'key': 'cart_review', 'label': 'Tagihan', 'component': 'cart_summary', 'can_go_back': True, 'on_complete': 'emit:cart_confirmed', 'props': {'show_table': True}},
                {'key': 'payment', 'label': 'Pembayaran', 'component': 'payment_method', 'can_go_back': True, 'on_complete': 'emit:payment_completed', 'props': {'methods': ['cash', 'qris', 'debit', 'midtrans'], 'split_bill': True}},
                {'key': 'receipt', 'label': 'Struk', 'component': 'receipt_display', 'can_go_back': False, 'on_complete': 'emit:receipt_done', 'props': {'print_enabled': True}},
            ]
        },
        'ui_schema': {'theme': 'restaurant', 'layout': 'table_view'},
        'default_settings': {
            'branding': {'primary_color': '#BF360C', 'app_name': 'Resto POS'},
            'features': {'kitchen_display': True, 'table_management': True},
            'regional': {'timezone': 'Asia/Jakarta', 'currency': 'IDR', 'locale': 'id-ID'},
        },
    },
]


class Command(BaseCommand):
    help = 'Seed all 8 business types into the database (idempotent)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            help='Seed a specific business type by code',
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate flow schema after seeding',
        )

    def handle(self, *args, **options):
        target_type = options.get('type')
        types_to_seed = (
            [bt for bt in BUSINESS_TYPES if bt['code'] == target_type]
            if target_type
            else BUSINESS_TYPES
        )

        if target_type and not types_to_seed:
            self.stderr.write(self.style.ERROR(f'Business type not found: {target_type}'))
            return

        count_created = 0
        count_updated = 0

        for bt_data in types_to_seed:
            obj, created = BusinessType.objects.update_or_create(
                code=bt_data['code'],
                defaults={
                    'name': bt_data['name'],
                    'icon': bt_data['icon'],
                    'version': bt_data['version'],
                    'flow_schema': bt_data['flow_schema'],
                    'ui_schema': bt_data['ui_schema'],
                    'default_settings': bt_data['default_settings'],
                    'is_active': True,
                },
            )
            if created:
                count_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {obj.name} ({obj.code} {obj.version})'))
            else:
                count_updated += 1
                self.stdout.write(f'Updated: {obj.name} ({obj.code} {obj.version})')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. {count_created} created, {count_updated} updated. '
                f'Total: {count_created + count_updated} business types seeded.'
            )
        )
