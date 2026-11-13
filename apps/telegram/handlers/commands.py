from telegram.ext import ConversationHandler

from apps.application.models import Application
from apps.telegram import states
from apps.telegram.handlers.registration import get_or_create_site_user
from apps.telegram.keyboards import replies


def start(update, context):
    get_or_create_site_user(update.message.from_user)
    context.user_data.clear()
    update.message.reply_text(
        "Assalomu alaykum! TIFT Clone qabul botiga xush kelibsiz.\n"
        "Ariza topshirish uchun telefon raqamingizni yuboring.",
        reply_markup=replies.get_contact(),
    )
    return states.PHONE


def cancel(update, context):
    context.user_data.clear()
    update.message.reply_text("Bekor qilindi. Qaytadan boshlash uchun /start.")
    return ConversationHandler.END


def status(update, context):
    user = get_or_create_site_user(update.message.from_user)
    application = Application.objects.filter(user=user).select_related("direction").first()
    if not application:
        update.message.reply_text("Sizda hali ariza yo'q. Topshirish uchun /start.")
        return
    update.message.reply_text(
        f"Ariza № {application.pk}\n"
        f"Yo'nalish: {application.direction.title if application.direction else '—'}\n"
        f"Holat: {application.get_status_display()}"
    )


def help(update, context):
    update.message.reply_text(
        "/start — ariza topshirish\n/status — ariza holati\n/cancel — joriy jarayonni bekor qilish"
    )
