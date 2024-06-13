from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from apps.Core.views import health_test

urlpatterns = [
    path('health_test/', health_test),
    path('admin/', admin.site.urls),
    path('', include(('apps.upload_crm.urls', 'apps.upload_crm'), namespace='upload_crm')),
]

if settings.DEV:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
