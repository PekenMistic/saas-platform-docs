import uuid
from functools import wraps
from django.db import models


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    tenant_id = models.UUIDField(db_index=True)
    user_id = models.UUIDField(null=True, blank=True)
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    before_data = models.JSONField(null=True, blank=True)
    after_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError('AuditLog cannot be edited')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError('AuditLog cannot be deleted')


def audit_action(action, entity_type):
    """Decorator that creates an audit log entry after a successful view call."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            try:
                tenant = getattr(request, 'tenant', None)
                if tenant:
                    AuditLog.objects.create(
                        tenant_id=tenant.id,
                        user_id=request.user.id if request.user.is_authenticated else None,
                        action=action,
                        entity_type=entity_type,
                        entity_id='',
                        ip_address=request.META.get('REMOTE_ADDR'),
                    )
            except Exception:
                pass
            return response
        return wrapper
    return decorator
