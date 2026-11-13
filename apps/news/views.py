from django.utils import timezone
from rest_framework.generics import ListAPIView, RetrieveAPIView

from apps.news.models import NewsContent
from apps.news.serializers import NewsContentDetailSerializer, NewsContentSerializer


def published_news():
    # Har so'rovda joriy vaqt bilan hisoblanadi. Avval queryset klass atributi edi va
    # timezone.now() server ishga tushgan paytda bir marta hisoblanardi.
    return NewsContent.objects.filter(is_published=True, publish_time__lte=timezone.now()).order_by("-publish_time", "-id")


class NewsContentListAPIView(ListAPIView):
    serializer_class = NewsContentSerializer

    def get_queryset(self):
        return published_news()


class NewsContentDetailAPIView(RetrieveAPIView):
    # Avval publish_time__gte edi (faqat kelajakdagi yangiliklar ochilardi) va matnsiz
    # serializer ishlatilardi.
    serializer_class = NewsContentDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return published_news()
