# TIFT Clone

Universitet sayti: fakultetlar va yo'nalishlar, yangiliklar, **onlayn qabul arizasi**
(sayt va Telegram bot orqali), qabul qilinganlar uchun avtomatik PDF shartnoma.

| Qism | Texnologiyalar |
|------|----------------|
| Backend | Django 5.2 · Django REST Framework · SimpleJWT · drf-yasg (Swagger) · CKEditor |
| Telegram bot | python-telegram-bot 13 (webhook) |
| PDF | WeasyPrint |
| Frontend | React 18 · TypeScript · Vite · Tailwind CSS · React Router · DOMPurify |

## Imkoniyatlar

- **Fakultetlar** — daraja bo'yicha filtr, dekan, yo'nalishlar (til, ta'lim shakli)
- **Yangiliklar** — faqat e'lon qilingan va vaqti kelganlari ko'rinadi
- **Onlayn ariza** — ro'yxatdan o'tish → forma (fakultet → yo'nalish, viloyat → tuman) → kabinetda holat
- **Telegram bot** — `/start` orqali xuddi shu arizani bosqichma-bosqich topshirish, `/status` — holat
- **Admin panel** — arizani "Qabul qilindi" qilinsa, shartnoma PDF avtomatik yaratiladi;
  arizachi uni kabinetdan yuklab oladi (faqat o'zinikini)

## Ishga tushirish

### Backend

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver          # http://localhost:8000  (admin: /admin/, API: /swagger/)
```

WeasyPrint uchun tizim kutubxonalari kerak bo'lishi mumkin (Ubuntu: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0`).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local          # BACKEND_URL=http://localhost:8000
npm run dev                          # http://localhost:5173
```

Fakultet, yo'nalish, viloyat/tuman va yangiliklarni admin paneldan (`/admin/`) qo'shing.

### Telegram bot

1. BotFather'dan token oling va `.env` ga `BOT_TOKEN` qilib yozing.
2. `TELEGRAM_WEBHOOK_SECRET` ga tasodifiy qiymat bering.
3. Webhook'ni ro'yxatdan o'tkazing (HTTPS manzil kerak, lokal uchun ngrok):
   ```bash
   curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<domen>/webhook/&secret_token=<SECRET>"
   ```

## API

| Method | URL | Tavsif |
|--------|-----|--------|
| POST | /api/v1/auth/register/ · /auth/login/ · /auth/refresh/ | Ro'yxatdan o'tish, JWT |
| GET | /api/v1/auth/me/ | Joriy foydalanuvchi |
| GET | /api/v1/faculties/?degree= · /faculties/{id}/ | Fakultetlar |
| GET | /api/v1/news/ · /news/{slug}/ | Yangiliklar |
| GET | /api/v1/regions/ · /regions/{id}/districts/ · /socials/ · /genders/ | Ma'lumotnomalar |
| POST | /api/v1/application-create/ | Ariza topshirish (login kerak, 1 foydalanuvchi — 1 ariza) |
| GET | /api/v1/application-status/ | O'z arizalari |
| GET | /api/v1/application-status/{id}/contract/ | Shartnoma PDF (faqat egasiga) |

To'liq hujjat: `/swagger/`.

## Testlar

```bash
DEBUG=1 python manage.py test apps
```

27 ta test: ariza API, ro'yxatdan o'tish, yangiliklar, shartnoma xavfsizligi va Telegram botning
to'liq ariza jarayoni (tarmoqqa chiqmasdan).

## Xavfsizlik eslatmalari

- `.env`, `db.sqlite3`, `media/`, `contracts/` git'ga kirmaydi — ularda maxfiy kalitlar va
  arizachilarning pasport ma'lumotlari bor.
- `django-ckeditor` (CKEditor 4) eskirgan va tuzatilmagan zaifliklari bor. Matnlarni faqat
  ishonchli adminlar kiritadi, frontend esa HTML'ni DOMPurify bilan tozalab ko'rsatadi.
  Kelajakda `django-ckeditor-5` ga o'tish tavsiya etiladi.
- Bot suhbat holatini jarayon xotirasida saqlaydi — bir nechta gunicorn worker bo'lsa,
  persistence qo'shish kerak.
