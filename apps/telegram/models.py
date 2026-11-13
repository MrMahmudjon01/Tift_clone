from django.db import models
from django.contrib.auth import get_user_model

User= get_user_model()


class TelegramUser(models.Model):
    telegram_id=models.BigIntegerField(unique=True)
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True,blank=True)
    first_name=models.CharField(max_length=255, null=True, blank=True)
    last_name=models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name or ''} {self.last_name or ''} ({self.telegram_id})".strip()
