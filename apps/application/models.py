import logging
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone

from apps.common.models import District
from apps.education.models import Direction

logger = logging.getLogger(__name__)


class Gender(models.TextChoices):
    MALE = "male", "Erkak"
    FEMALE = "female", "Ayol"


class ApplicationStatusChoices(models.TextChoices):
    PENDING = "pending", "Ko'rib chiqilmoqda"
    ACCEPTED = "accepted", "Qabul qilindi"
    REJECTED = "rejected", "Rad etildi"


class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="applications")
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    # unique emas: eski bazada dublikatlar bor. Takrorlanish serializer va botda tekshiriladi.
    passport = models.CharField(max_length=9, db_index=True)
    pinfl = models.CharField(max_length=14)
    gender = models.CharField(max_length=6, choices=Gender.choices)
    birth_date = models.DateField()
    direction = models.ForeignKey(Direction, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=16, choices=ApplicationStatusChoices.choices,
                              default=ApplicationStatusChoices.PENDING)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    # CONTRACT_ROOT ga nisbatan fayl nomi (ommaga ochiq URL emas)
    contract_url = models.CharField(max_length=255, null=True, blank=True)

    accepted_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def contract_path(self):
        return settings.CONTRACT_ROOT / self.contract_url if self.contract_url else None

    def generate_contract(self) -> str:
        """Shartnoma PDF'ini shablondan to'g'ridan-to'g'ri yaratadi.

        Avval PDF o'z serverining ommaga ochiq /student-application?application_id=N
        sahifasidan HTTP orqali olinardi (u sahifa login'siz har kimga pasport/JSHSHIR
        ko'rsatardi), fayl nomi esa foydalanuvchi ismidan yasalardi (../ bilan papkadan
        chiqib ketish mumkin edi). Endi nom — tasodifiy UUID.
        """
        from weasyprint import HTML

        settings.CONTRACT_ROOT.mkdir(parents=True, exist_ok=True)
        file_name = f"{uuid.uuid4().hex}.pdf"
        html = render_to_string("application.html", {"application": self})
        HTML(string=html).write_pdf(settings.CONTRACT_ROOT / file_name)
        return file_name

    def save(self, *args, **kwargs) -> None:
        decided = self.status in (ApplicationStatusChoices.ACCEPTED, ApplicationStatusChoices.REJECTED)
        if decided and not self.accepted_at:
            if self.status == ApplicationStatusChoices.ACCEPTED:
                try:
                    self.contract_url = self.generate_contract()
                except Exception:  # PDF yaratilmasa ham status saqlansin
                    logger.exception("Shartnoma yaratilmadi (ariza %s)", self.pk)
            self.accepted_at = timezone.now()
        return super().save(*args, **kwargs)
