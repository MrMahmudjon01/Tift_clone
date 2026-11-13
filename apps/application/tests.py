import json
import shutil
import tempfile
from unittest import mock

from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.application.models import Application, ApplicationStatusChoices, Gender
from apps.common.models import District, Region
from apps.education.models import Direction, Faculty
from apps.telegram.models import TelegramUser


def make_refs():
    faculty = Faculty.objects.create(title="Muhandislik", body="-", degree="bachelors")
    direction = Direction.objects.create(title="Matematika", faculty=faculty, body="-",
                                         language="uz", education_type="daytime")
    region = Region.objects.create(title="Toshkent viloyati", order_id=1)
    district = District.objects.create(title="Chirchiq", region=region, order_id=1)
    return faculty, direction, region, district


class ApplicationAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Kuchli-parol-2026')
        self.client.force_authenticate(self.user)
        self.faculty, self.direction, self.region, self.district = make_refs()
        self.data = {
            "first_name": "John", "last_name": "Doe", "passport": "AB1234567",
            "pinfl": "12345678901234", "gender": Gender.MALE, "birth_date": "2005-01-01",
            "direction": self.direction.id, "district": self.district.id,
        }

    def _create(self, user=None, **over):
        fields = {**self.data, "direction": self.direction, "district": self.district, **over}
        return Application.objects.create(user=user or self.user, **fields)

    def test_application_create(self):
        r = self.client.post(reverse('application-create'), self.data, format='json')
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.data)
        app = Application.objects.get()
        self.assertEqual((app.first_name, app.status, app.user), ("John", "pending", self.user))
        self.assertEqual(str(app), "John Doe")  # avval "(self.first_name) (self.last_name)" qaytarardi

    def test_duplicate_passport_rejected(self):
        other = User.objects.create_user(username='other', password='Kuchli-parol-2026')
        self._create(user=other)
        r = self.client.post(reverse('application-create'), self.data, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("passport", r.data)

    def test_one_application_per_user(self):
        self._create(passport="AA0000001")
        r = self.client.post(reverse('application-create'), self.data, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_passport_and_pinfl(self):
        r = self.client.post(reverse('application-create'),
                             {**self.data, "passport": "12345", "pinfl": "abc"}, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("passport", r.data)
        self.assertIn("pinfl", r.data)

    def test_missing_field(self):
        data = {k: v for k, v in self.data.items() if k != "first_name"}
        r = self.client.post(reverse('application-create'), data, format='json')
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', r.data)

    def test_unauthenticated(self):
        self.client.force_authenticate(None)
        r = self.client.post(reverse('application-create'), self.data, format='json')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_status_list_only_own(self):
        self._create()
        other = User.objects.create_user(username='other', password='Kuchli-parol-2026')
        self._create(user=other, passport="AA7654321")
        r = self.client.get(reverse('application-status'))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data['count'], 1)
        row = r.data['results'][0]
        self.assertEqual(row['status'], "Ko'rib chiqilmoqda")
        self.assertEqual(row['direction']['title'], "Matematika")  # avval DistrictsSerializer edi

    def test_status_list_empty(self):
        r = self.client.get(reverse('application-status'))
        self.assertEqual(r.data['count'], 0)


class ContractSecurityTestCase(APITestCase):
    """Pasport ma'lumotlari va shartnomalar faqat egasi/xodimga ko'rinishi kerak."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        override = override_settings(CONTRACT_ROOT=__import__('pathlib').Path(self.tmp))
        override.enable()
        self.addCleanup(override.disable)
        _, direction, _, district = make_refs()
        self.owner = User.objects.create_user(username='owner', password='Kuchli-parol-2026')
        self.app = Application.objects.create(
            user=self.owner, first_name="Ali", last_name="../../../tmp/hack", passport="AB1112223",
            pinfl="11122233344455", gender="male", birth_date="2005-05-05",
            direction=direction, district=district,
        )

    def test_guest_cannot_view_application_page(self):
        r = self.client.get(f"/student-application?application_id={self.app.pk}")
        self.assertEqual(r.status_code, 302)  # login sahifasiga
        self.assertNotIn(b"AB1112223", r.content)

    def test_staff_can_view_application_page(self):
        staff = User.objects.create_user(username='staff', password='x', is_staff=True)
        self.client.force_login(staff)
        r = self.client.get(f"/student-application?application_id={self.app.pk}")
        self.assertEqual(r.status_code, 200)
        self.assertIn(b"AB1112223", r.content)

    def test_contract_file_name_is_not_user_controlled(self):
        with mock.patch("weasyprint.HTML") as html:
            self.app.status = ApplicationStatusChoices.ACCEPTED
            self.app.save()
        self.assertRegex(self.app.contract_url, r"^[0-9a-f]{32}\.pdf$")
        html.return_value.write_pdf.assert_called_once()
        self.assertIsNotNone(self.app.accepted_at)

    def test_contract_download_owner_only(self):
        self.app.contract_url = "c.pdf"
        self.app.save(update_fields=["contract_url"])
        (__import__('pathlib').Path(self.tmp) / "c.pdf").write_bytes(b"%PDF-1.4 test")
        url = reverse('application-contract', args=[self.app.pk])

        stranger = User.objects.create_user(username='stranger', password='Kuchli-parol-2026')
        self.client.force_authenticate(stranger)
        self.assertEqual(self.client.get(url).status_code, 404)

        self.client.force_authenticate(self.owner)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(b"".join(r.streaming_content), b"%PDF-1.4 test")


@override_settings(BOT_TOKEN="123456789:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", TELEGRAM_WEBHOOK_SECRET="s3cret")
class TelegramWebhookTestCase(APITestCase):
    """Bot orqali to'liq ariza jarayoni (avval oxirida ariza saqlanmasdi)."""

    def setUp(self):
        from apps.telegram.dispatcher import get_dispatcher
        get_dispatcher.cache_clear()
        self.addCleanup(get_dispatcher.cache_clear)
        self.faculty, self.direction, self.region, self.district = make_refs()
        # Testlar tarmoqqa chiqmasligi kerak: bot nomi (get_me) va xabar yuborish soxtalashtiriladi
        from telegram import User as TgUser
        for target, kwargs in [("telegram.Bot.get_me", {"return_value": TgUser(1, "bot", True, username="test_bot")})]:
            p = mock.patch(target, **kwargs); p.start(); self.addCleanup(p.stop)
        patcher = mock.patch("telegram.Bot.send_message")
        self.sent = patcher.start()
        self.addCleanup(patcher.stop)
        self.update_id = 0

    def _send(self, text=None, contact=None, secret="s3cret"):
        self.update_id += 1
        message = {"message_id": self.update_id, "date": 0,
                   "chat": {"id": 555, "type": "private"},
                   "from": {"id": 555, "is_bot": False, "first_name": "Ali"}}
        if contact:
            message["contact"] = contact
        else:
            message["text"] = text
            if text.startswith("/"):
                message["entities"] = [{"type": "bot_command", "offset": 0, "length": len(text)}]
        return self.client.post("/webhook/", json.dumps({"update_id": self.update_id, "message": message}),
                                content_type="application/json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN=secret)

    def last_reply(self):
        return self.sent.call_args.kwargs.get("text") or self.sent.call_args.args[1]

    def test_rejects_requests_without_secret(self):
        self.assertEqual(self._send("/start", secret="wrong").status_code, 403)
        self.sent.assert_not_called()

    def test_full_registration_creates_application(self):
        steps = [
            ("/start", None),
            (None, {"phone_number": "+998901234567", "first_name": "Ali", "user_id": 555}),
            ("Ali Valiyev", None),
            ("ab1234567", None),
            ("12345678901234", None),
            ("Erkak", None),
            ("15.03.2006", None),
            ("Muhandislik", None),
            ("Matematika", None),
            ("Toshkent viloyati", None),
            ("Chirchiq", None),
        ]
        for text, contact in steps:
            self.assertEqual(self._send(text, contact).status_code, 200)
        app = Application.objects.get()
        self.assertEqual((app.first_name, app.last_name, app.passport), ("Ali", "Valiyev", "AB1234567"))
        self.assertEqual((app.direction, app.district), (self.direction, self.district))
        self.assertEqual(TelegramUser.objects.get(telegram_id=555).user, app.user)
        self.assertIn("qabul qilindi", self.last_reply())

        # Qayta /start — ikkinchi ariza yaratilmaydi, bot yiqilmaydi (avval states.END xatosi)
        self._send("/start")
        self._send(None, {"phone_number": "+998901234567", "first_name": "Ali", "user_id": 555})
        self.assertEqual(Application.objects.count(), 1)
        self.assertIn("allaqachon", self.last_reply())

    def test_invalid_pinfl_does_not_crash(self):
        for text, contact in [("/start", None),
                              (None, {"phone_number": "+998901234567", "first_name": "Ali", "user_id": 555}),
                              ("Ali Valiyev", None), ("AB1234567", None), ("123", None)]:
            self._send(text, contact)
        self.assertIn("14 ta raqam", self.last_reply())  # avval states.PINFL AttributeError
