from functools import wraps
from django.core.exceptions import PermissionDenied


def require_tenant_context(view_func):
    """Decorator that enforces tenant context on every view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'tenant') or not request.tenant:
            raise PermissionDenied('Tenant context not found')
        if not request.tenant.is_active:
            raise PermissionDenied('Tenant is not active')
        return view_func(request, *args, **kwargs)
    return wrapper


def require_roles(*roles):
    """Decorator that enforces role-based access on DRF views."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                raise PermissionDenied('Authentication required')
            user_role = getattr(request.user, 'role', None)
            if user_role not in roles:
                raise PermissionDenied(
                    f'Role {user_role!r} not allowed. Required: {roles}'
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
