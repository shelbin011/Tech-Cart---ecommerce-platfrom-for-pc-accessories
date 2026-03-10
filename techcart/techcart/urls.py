from django.contrib import admin
from django.urls import path, include
from customer_app import views as customer_views
from admin_app import views as admin_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', include('admin_app.urls')),
    path('django_admin/', admin.site.urls),
    path('', customer_views.home, name='root'), # Map root URL to home
    path('', include('customer_app.urls')), # Include all customer URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
