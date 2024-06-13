from django.urls import path

from apps.upload_crm.controllers.amo import upload_amo

urlpatterns = [
    path('upload_amo/', upload_amo),
]
