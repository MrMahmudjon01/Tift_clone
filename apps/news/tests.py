from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import NewsContent
from datetime import datetime


class NewsContentAPITestCase(APITestCase):
    def setUp(self):
        self.item_active = NewsContent.objects.create(
            title="test news",
            body="test news test",
            is_published=True,
            publish_time=datetime(2024, 8, 29, 12, 30, 30),
        )

        self.item_inactive = NewsContent.objects.create(
            title="test news",
            body="test news test",
            is_published=False,
            publish_time=datetime(2024, 8, 31, 12, 30, 30),
        )

        self.list_url = reverse('news-list')

    def test_news_content_list_api(self):
        response = self.client.get(self.list_url)
        data = response.json()
        count = data.get("count")

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, count)
        self.assertEqual(self.item_active.title, data['results'][0]['title'])
        self.assertEqual(self.item_active.slug, data['results'][0]['slug'])


class NewsDetailRegressionTest(APITestCase):
    """Avval detail faqat KELAJAKDAGI yangiliklarni ochardi va matnni (body) qaytarmasdi."""

    def test_published_news_detail_has_body(self):
        from django.utils import timezone
        past = NewsContent.objects.create(title="O'tgan yangilik", body="<p>Matn</p>", is_published=True,
                                          publish_time=timezone.now() - timezone.timedelta(days=1))
        future = NewsContent.objects.create(title="Kelajak", body="x", is_published=True,
                                            publish_time=timezone.now() + timezone.timedelta(days=1))
        r = self.client.get(f"/api/v1/news/{past.slug}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["body"], "<p>Matn</p>")
        self.assertEqual(self.client.get(f"/api/v1/news/{future.slug}/").status_code, 404)

    def test_unicode_title_gets_non_empty_unique_slug(self):
        from django.utils import timezone
        a = NewsContent.objects.create(title="Янгилик", body="x", publish_time=timezone.now())
        b = NewsContent.objects.create(title="Янгилик", body="x", publish_time=timezone.now())
        self.assertTrue(a.slug)
        self.assertNotEqual(a.slug, b.slug)
