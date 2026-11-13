from django.urls import path

from apps.application.views import (
    ApplicationContractDownloadAPIView,
    ApplicationCreateAPIView,
    ApplicationStatusesListAPIView,
)

urlpatterns = [
    path("application-create/", ApplicationCreateAPIView.as_view(), name='application-create'),
    path("application-status/", ApplicationStatusesListAPIView.as_view(), name='application-status'),
    path("application-status/<int:pk>/contract/", ApplicationContractDownloadAPIView.as_view(),
         name='application-contract'),
]
