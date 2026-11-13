from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class AuthAPITestCase(APITestCase):
    def test_register_login_me(self):
        r = self.client.post("/api/v1/auth/register/", {"username": "ali", "password": "Kuchli-parol-2026"})
        self.assertEqual(r.status_code, 201, r.data)
        self.assertIn("access", r.data)
        r = self.client.post("/api/v1/auth/login/", {"username": "ali", "password": "Kuchli-parol-2026"})
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])
        r = self.client.get("/api/v1/auth/me/")
        self.assertEqual((r.data["username"], r.data["has_application"]), ("ali", False))

    def test_weak_password_and_duplicate_username(self):
        self.assertEqual(self.client.post("/api/v1/auth/register/",
                                          {"username": "vali", "password": "12345678"}).status_code, 400)
        User.objects.create_user(username="Vali", password="x")
        r = self.client.post("/api/v1/auth/register/", {"username": "vali", "password": "Kuchli-parol-2026"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("username", r.data)

    def test_telegram_users_cannot_login_with_password(self):
        u = User.objects.create(username="tg_555")
        u.set_unusable_password(); u.save()
        r = self.client.post("/api/v1/auth/login/", {"username": "tg_555", "password": ""})
        self.assertEqual(r.status_code, 400)
