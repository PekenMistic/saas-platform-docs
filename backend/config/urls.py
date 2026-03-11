from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('health/', include('apps.core.urls.health')),
    path('api/v1/', include([
        path('auth/', include('apps.core.urls.auth')),
        path('tenants/', include('apps.tenants.urls')),
        path('flow/', include('apps.flow_engine.urls')),
        path('products/', include('apps.products.urls')),
        path('transactions/', include('apps.transactions.urls')),
        path('sync/', include('apps.sync.urls')),
        path('payments/', include('apps.payments.urls')),
        path('notifications/', include('apps.notifications.urls')),
        path('reports/', include('apps.reports.urls')),
    ])),
]
