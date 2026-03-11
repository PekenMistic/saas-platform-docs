from rest_framework.permissions import BasePermission

ROLE_HIERARCHY = {
    'public': 0,
    'customer': 1,
    'cashier': 2,
    'supervisor': 3,
    'branch_manager': 4,
    'tenant_admin': 5,
    'tenant_owner': 6,
    'saas_admin': 7,
}


class HasTenantContext(BasePermission):
    """Ensures the request has a valid, active tenant attached."""

    message = 'Tenant context is required.'

    def has_permission(self, request, view):
        tenant = getattr(request, 'tenant', None)
        return bool(tenant and tenant.is_active)


class IsCashierOrAbove(BasePermission):
    message = 'Cashier role or above required.'

    def has_permission(self, request, view):
        role = getattr(request.user, 'role', 'public')
        return ROLE_HIERARCHY.get(role, 0) >= ROLE_HIERARCHY['cashier']


class IsBranchManagerOrAbove(BasePermission):
    message = 'Branch manager role or above required.'

    def has_permission(self, request, view):
        role = getattr(request.user, 'role', 'public')
        return ROLE_HIERARCHY.get(role, 0) >= ROLE_HIERARCHY['branch_manager']


class IsTenantAdminOrAbove(BasePermission):
    message = 'Tenant admin role or above required.'

    def has_permission(self, request, view):
        role = getattr(request.user, 'role', 'public')
        return ROLE_HIERARCHY.get(role, 0) >= ROLE_HIERARCHY['tenant_admin']


class IsSaaSAdmin(BasePermission):
    message = 'SaaS admin role required.'

    def has_permission(self, request, view):
        role = getattr(request.user, 'role', 'public')
        return ROLE_HIERARCHY.get(role, 0) >= ROLE_HIERARCHY['saas_admin']


def permission_required(permission_code):
    """Simple decorator for checking role-based permissions on function-based views."""
    from functools import wraps
    from django.core.exceptions import PermissionDenied

    PERMISSION_ROLE_MAP = {
        'pos:read': 'cashier',
        'pos:write': 'cashier',
        'stock:read': 'cashier',
        'stock:write': 'supervisor',
        'products:read': 'cashier',
        'products:write': 'branch_manager',
        'reports:read': 'branch_manager',
        'settings:write': 'tenant_admin',
        'tenants:manage': 'saas_admin',
    }

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            required_role = PERMISSION_ROLE_MAP.get(permission_code, 'saas_admin')
            user_role = getattr(request.user, 'role', 'public')
            if ROLE_HIERARCHY.get(user_role, 0) < ROLE_HIERARCHY.get(required_role, 99):
                raise PermissionDenied(f'Permission denied: {permission_code}')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
