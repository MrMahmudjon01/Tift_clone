import hmac
import json
import logging

from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from telegram import Update

from apps.telegram.dispatcher import get_dispatcher

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def message_handler(request):
    """Telegram webhook.

    Avval: so'rov kimdan kelganini tekshirmasdi (istalgan odam soxta xabar yubora olardi),
    har bir xabarni (pasport ma'lumotlari bilan) print() qilardi va noto'g'ri JSON da 500 berardi.
    """
    secret = settings.TELEGRAM_WEBHOOK_SECRET
    if secret:
        received = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not hmac.compare_digest(received, secret):
            return HttpResponseForbidden()
    try:
        payload = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return HttpResponseBadRequest()

    dispatcher = get_dispatcher()
    try:
        dispatcher.process_update(Update.de_json(payload, dispatcher.bot))
    except Exception:
        logger.exception("Telegram update qayta ishlanmadi (update_id=%s)", payload.get("update_id"))
    return JsonResponse({"ok": True})
