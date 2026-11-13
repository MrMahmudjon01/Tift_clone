from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from apps.application.views import StudentApplicationTemplateview
from apps.telegram.views import message_handler

schema_view = get_schema_view(
    openapi.Info(
        title="TIFT Clone API",
        default_version='v1',
        description="Fakultetlar, yo'nalishlar, yangiliklar va qabul arizalari API'si",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('webhook/', message_handler, name='telegram-webhook'),
    # Shartnoma shablonini ko'rish — faqat xodimlar (staff) uchun
    path("student-application", StudentApplicationTemplateview.as_view(), name="application_generator"),
    path('admin/', admin.site.urls),
    path("api/v1/", include("apps.users.urls")),
    path("api/v1/", include("apps.news.urls")),
    path("api/v1/", include("apps.education.urls")),
    path("api/v1/", include("apps.application.urls")),
    path("api/v1/", include("apps.common.urls")),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    # Shartnomalar (contracts/) bu yerda ATAYLAB ochilmaydi — ular faqat API orqali egasiga beriladi
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
