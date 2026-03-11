from django.urls import path
from apps.core.auth.views import TenantLoginView, TenantTokenRefreshView, logout_view, me_view

urlpatterns = [
    path('login/', TenantLoginView.as_view(), name='auth-login'),
    path('refresh/', TenantTokenRefreshView.as_view(), name='auth-refresh'),
    path('logout/', logout_view, name='auth-logout'),
    path('me/', me_view, name='auth-me'),
]
