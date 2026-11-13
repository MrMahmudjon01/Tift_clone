"""Telegram orqali qabul arizasini topshirish (ConversationHandler bosqichlari).

Avvalgi versiyadagi xatolar: ariza oxirida bazaga saqlanmasdi; mavjud bo'lmagan
holatlarga (states.END, states.PINFL, states.BIRTH_DATE) qaytilib bot yiqilardi;
takroriy ariza tekshiruvi Telegram ID ni Django user ID bilan solishtirardi.
"""
import re
from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from apps.application.models import Application
from apps.common.models import District, Region
from apps.education.models import Direction, Faculty
from apps.telegram import states
from apps.telegram.keyboards import replies
from apps.telegram.models import TelegramUser

User = get_user_model()

PASSPORT_RE = re.compile(r"^[A-Z]{2}\d{7}$")
PINFL_RE = re.compile(r"^\d{14}$")
GENDERS = {"Erkak": "male", "Ayol": "female"}


def get_or_create_site_user(tg_user) -> User:
    """Telegram foydalanuvchisiga bog'langan Django foydalanuvchisi (ariza egasi)."""
    tg, _ = TelegramUser.objects.get_or_create(
        telegram_id=tg_user.id,
        defaults={"first_name": tg_user.first_name, "last_name": tg_user.last_name},
    )
    if tg.user_id is None:
        user, created = User.objects.get_or_create(username=f"tg_{tg_user.id}")
        if created:
            user.set_unusable_password()  # saytga parol bilan kira olmaydi
            user.save(update_fields=["password"])
        tg.user = user
        tg.save(update_fields=["user"])
    return tg.user


def _text(update):
    return (update.message.text or "").strip() if update.message else ""


def get_phone(update, context):
    msg = update.message
    if msg and msg.contact:
        if Application.objects.filter(user=get_or_create_site_user(msg.from_user)).exists():
            msg.reply_text("Siz allaqachon ariza topshirgansiz. Holatini saytdagi shaxsiy kabinetda "
                           "yoki /status buyrug'i orqali ko'rishingiz mumkin.", reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        if msg.contact.user_id != msg.from_user.id:
            msg.reply_text("Bu raqam sizga tegishli emas. Iltimos, tugma orqali o'z raqamingizni yuboring.",
                           reply_markup=replies.get_contact())
            return states.PHONE
        context.user_data["phone"] = msg.contact.phone_number
        msg.reply_text("Rahmat! Endi ism va familiyangizni yuboring (masalan: Ali Valiyev).",
                       reply_markup=ReplyKeyboardRemove())
        return states.FULL_NAME
    msg.reply_text("Iltimos, telefon raqamingizni pastdagi tugma orqali yuboring.",
                   reply_markup=replies.get_contact())
    return states.PHONE


def get_full_name(update, context):
    parts = _text(update).split()
    if len(parts) >= 2 and all(len(p) <= 100 for p in parts):
        context.user_data["first_name"] = parts[0]
        context.user_data["last_name"] = " ".join(parts[1:])
        update.message.reply_text("Pasport seriya va raqamini AA1234567 formatida yuboring.")
        return states.PASSPORT
    update.message.reply_text("Ism va familiyangizni bitta xabarda yuboring (masalan: Ali Valiyev).")
    return states.FULL_NAME


def get_passport(update, context):
    text = _text(update).upper().replace(" ", "")
    if PASSPORT_RE.match(text):
        if Application.objects.filter(passport=text).exists():
            update.message.reply_text("Bu pasport bilan ariza allaqachon topshirilgan.")
            return states.PASSPORT
        context.user_data["passport"] = text
        update.message.reply_text("To'g'ri. Endi JSHSHIR (PINFL, 14 ta raqam) ni yuboring.")
        return states.PINFIL
    update.message.reply_text("Pasportni AA1234567 formatida yuboring.")
    return states.PASSPORT


def get_pinfil(update, context):
    text = _text(update).replace(" ", "")
    if PINFL_RE.match(text):
        context.user_data["pinfl"] = text
        update.message.reply_text("Jinsingizni tanlang.", reply_markup=replies.get_gender())
        return states.GENDER
    update.message.reply_text("JSHSHIR 14 ta raqamdan iborat bo'lishi kerak.")
    return states.PINFIL


def get_gender(update, context):
    text = _text(update)
    if text in GENDERS:
        context.user_data["gender"] = GENDERS[text]
        update.message.reply_text("Tug'ilgan sanangizni KK.OO.YYYY formatida yuboring (masalan: 15.03.2006).",
                                  reply_markup=ReplyKeyboardRemove())
        return states.BIRTH_DATA
    update.message.reply_text("Iltimos, pastdagi tugmalardan birini tanlang.", reply_markup=replies.get_gender())
    return states.GENDER


def get_birth_date(update, context):
    try:
        birth_date = datetime.strptime(_text(update), "%d.%m.%Y").date()
    except ValueError:
        birth_date = None
    today = date.today()
    if birth_date and date(1950, 1, 1) <= birth_date <= today.replace(year=today.year - 14):
        context.user_data["birth_date"] = birth_date
        update.message.reply_text("Fakultetni tanlang.",
                                  reply_markup=replies.get_items(Faculty.objects.all(), "title"))
        return states.FACULTY
    update.message.reply_text("Sanani KK.OO.YYYY formatida yuboring (masalan: 15.03.2006).")
    return states.BIRTH_DATA


def get_faculty(update, context):
    faculty = Faculty.objects.filter(title=_text(update)).first()
    if faculty:
        context.user_data["faculty"] = faculty.id
        update.message.reply_text("Yo'nalishni tanlang.",
                                  reply_markup=replies.get_items(faculty.directions.all(), "title"))
        return states.DIRECTION
    update.message.reply_text("Ro'yxatdagi fakultetlardan birini tanlang.",
                              reply_markup=replies.get_items(Faculty.objects.all(), "title"))
    return states.FACULTY


def get_direction(update, context):
    faculty = Faculty.objects.filter(id=context.user_data.get("faculty")).first()
    if not faculty:
        update.message.reply_text("Fakultetni qaytadan tanlang.",
                                  reply_markup=replies.get_items(Faculty.objects.all(), "title"))
        return states.FACULTY
    direction = faculty.directions.filter(title=_text(update)).first()
    if direction:
        context.user_data["direction"] = direction.id
        update.message.reply_text("Viloyatni tanlang.", reply_markup=replies.get_items(Region.objects.all(), "title"))
        return states.REGION
    update.message.reply_text("Ro'yxatdagi yo'nalishlardan birini tanlang.",
                              reply_markup=replies.get_items(faculty.directions.all(), "title"))
    return states.DIRECTION


def get_region(update, context):
    region = Region.objects.filter(title=_text(update)).first()
    if region:
        context.user_data["region"] = region.id
        update.message.reply_text("Tumanni tanlang.", reply_markup=replies.get_items(region.districts.all(), "title"))
        return states.DISTRICT
    update.message.reply_text("Ro'yxatdagi viloyatlardan birini tanlang.",
                              reply_markup=replies.get_items(Region.objects.all(), "title"))
    return states.REGION


def get_district(update, context):
    region = Region.objects.filter(id=context.user_data.get("region")).first()
    district = region.districts.filter(title=_text(update)).first() if region else None
    if not district:
        update.message.reply_text("Ro'yxatdagi tumanlardan birini tanlang.",
                                  reply_markup=replies.get_items(region.districts.all(), "title") if region else None)
        return states.DISTRICT

    data = context.user_data
    if Application.objects.filter(passport=data.get("passport")).exists():
        update.message.reply_text("Bu pasport bilan ariza allaqachon topshirilgan.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    try:
        with transaction.atomic():
            application = Application.objects.create(
                user=get_or_create_site_user(update.message.from_user),
                first_name=data["first_name"], last_name=data["last_name"],
                passport=data["passport"], pinfl=data["pinfl"], gender=data["gender"],
                birth_date=data["birth_date"], direction=Direction.objects.filter(id=data["direction"]).first(),
                district=district,
            )
    except KeyError:
        update.message.reply_text("Ma'lumotlar to'liq emas. /start bilan qaytadan boshlang.",
                                  reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    context.user_data.clear()
    update.message.reply_text(
        f"✅ Arizangiz qabul qilindi! Ariza raqami: {application.pk}.\n"
        "Holatini /status buyrug'i orqali kuzatishingiz mumkin.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
