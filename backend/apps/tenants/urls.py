from django.urls import path
from apps.tenants.views import (
    TenantListCreateView,
    TenantDetailView,
    current_tenant_view,
    BusinessTypeListView,
)

urlpatterns = [
    path('', TenantListCreateView.as_view(), name='tenant-list'),
    path('<uuid:pk>/', TenantDetailView.as_view(), name='tenant-detail'),
    path('current/', current_tenant_view, name='tenant-current'),
    path('business-types/', BusinessTypeListView.as_view(), name='business-type-list'),
]
