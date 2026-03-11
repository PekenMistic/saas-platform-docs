from django.urls import path
from django.http import JsonResponse
from django.db import connection


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        db_ok = True
    except Exception:
        db_ok = False

    payload = {
        'status': 'ok' if db_ok else 'degraded',
        'database': 'ok' if db_ok else 'error',
    }
    http_status = 200 if db_ok else 503
    return JsonResponse(payload, status=http_status)


urlpatterns = [
    path('', health_check, name='health-check'),
]
