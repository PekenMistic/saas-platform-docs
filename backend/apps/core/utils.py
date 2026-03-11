import hashlib
import hmac
import uuid
from django.conf import settings


def generate_sync_checksum(payload: dict) -> str:
    """Generate HMAC-SHA256 checksum for sync payload verification."""
    import json
    secret = settings.SYNC_SECRET_KEY.encode()
    data = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    return hmac.new(secret, data, hashlib.sha256).hexdigest()


def verify_sync_checksum(payload: dict, provided_checksum: str) -> bool:
    """Verify sync payload checksum."""
    expected = generate_sync_checksum(payload)
    return hmac.compare_digest(expected, provided_checksum)


def get_client_ip(request) -> str:
    """Extract client IP from request, respecting proxy headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def generate_transaction_number(branch_code: str, sequence: int) -> str:
    """Generate human-readable transaction number."""
    from django.utils import timezone
    date_str = timezone.now().strftime('%Y%m%d')
    return f'TRX-{date_str}-{branch_code}-{sequence:04d}'
