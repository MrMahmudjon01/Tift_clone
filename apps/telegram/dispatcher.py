from functools import lru_cache

from django.conf import settings
from telegram import Bot
from telegram.ext import CommandHandler, ConversationHandler, Dispatcher, Filters, MessageHandler

from apps.telegram import states
from apps.telegram.handlers import commands, registration


@lru_cache(maxsize=1)
def get_dispatcher() -> Dispatcher:
    """Dispatcher birinchi webhook so'rovida yaratiladi.

    Avval modul import qilinishi bilan Bot(token) yaratilardi — BOT_TOKEN bo'lmasa
    butun sayt (urls.py) ishga tushmasdi.

    Eslatma: suhbat holati jarayon xotirasida saqlanadi. Bir nechta gunicorn worker
    ishlatilsa, persistence (masalan PicklePersistence) qo'shish kerak.
    """
    bot = Bot(token=settings.BOT_TOKEN)
    dispatcher = Dispatcher(bot, None, workers=0)
    text = Filters.text & ~Filters.command
    dispatcher.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", commands.start)],
        states={
            states.PHONE: [MessageHandler(Filters.contact | text, registration.get_phone)],
            states.FULL_NAME: [MessageHandler(text, registration.get_full_name)],
            states.PASSPORT: [MessageHandler(text, registration.get_passport)],
            states.PINFIL: [MessageHandler(text, registration.get_pinfil)],
            states.GENDER: [MessageHandler(text, registration.get_gender)],
            states.BIRTH_DATA: [MessageHandler(text, registration.get_birth_date)],
            states.FACULTY: [MessageHandler(text, registration.get_faculty)],
            states.DIRECTION: [MessageHandler(text, registration.get_direction)],
            states.REGION: [MessageHandler(text, registration.get_region)],
            states.DISTRICT: [MessageHandler(text, registration.get_district)],
        },
        fallbacks=[CommandHandler("start", commands.start), CommandHandler("cancel", commands.cancel)],
    ))
    dispatcher.add_handler(CommandHandler("status", commands.status))
    dispatcher.add_handler(CommandHandler("help", commands.help))
    # Avval har qanday xabarni aks-sado qilib qaytaruvchi echo handler bor edi
    dispatcher.add_handler(MessageHandler(Filters.all, commands.help))
    return dispatcher
