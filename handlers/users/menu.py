import datetime
from aiogram import F, types, Bot
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from zoneinfo import ZoneInfo
from routers import users as router

GROUP_ID = -1003898804487
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")


def tz_now() -> datetime.datetime:
    """Always return timezone-aware current time"""
    return datetime.datetime.now(TASHKENT_TZ)


def make_tz(dt: datetime.datetime) -> datetime.datetime:
    """Attach Tashkent timezone if datetime is naive"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TASHKENT_TZ)
    return dt.astimezone(TASHKENT_TZ)


def parse_booking_datetime(date_str: str, time_str: str) -> datetime.datetime:
    """Create timezone-aware booking datetime"""
    naive = datetime.datetime.strptime(
        f"{date_str} {time_str}",
        "%Y-%m-%d %H:%M"
    )
    return naive.replace(tzinfo=TASHKENT_TZ)

def ensure_tz(dt: datetime.datetime) -> datetime.datetime:
    """
    Guarantee datetime is Asia/Tashkent aware.
    Works for:
    - naive datetime
    - UTC datetime
    - already aware datetime
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TASHKENT_TZ)

    return dt.astimezone(TASHKENT_TZ)


# =========================
# ASOSIY MENU
# =========================

async def button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚗 Xizmatlarni ko‘rish")],
            [
                KeyboardButton(text="📅 Navbatga yozilish"),
                KeyboardButton(text="🛠 Mening buyurtmalarim")
            ],
            [
                KeyboardButton(text="📍 Lokatsiya"),
                KeyboardButton(text="📞 Kontakt")
            ],
            [KeyboardButton(text="💬 Murojaat yuborish")]
        ],
        resize_keyboard=True
    )


# =========================
# XIZMATLAR
# =========================

SERVICES = [
    {"title": "Dvigatel diagnostikasi", "price": 150000},
    {"title": "Moy almashtirish", "price": 80000},
    {"title": "Tormoz kolodkasi almashtirish", "price": 120000},
    {"title": "Akkumulyator almashtirish", "price": 200000},
    {"title": "Kompyuter diagnostika", "price": 100000},
]


# =========================
# STORAGE
# =========================

BOOKINGS = {}
BOOKED_SLOTS = {}
USER_BOOKINGS = {}
COMPLETED_BOOKINGS = []
BOOKING_COUNTER = 1


# =========================
# STATES
# =========================

class BookingState(StatesGroup):
    choosing_date = State()
    choosing_time = State()
    confirming = State()

class ContactState(StatesGroup):
    waiting_message = State()


# =========================
# UTIL FUNKSIYALAR
# =========================

def generate_dates_keyboard():
    today = datetime.datetime.now(TASHKENT_TZ).date()
    keyboard = []

    for i in range(15):
        day = today + datetime.timedelta(days=i)
        formatted = day.strftime("%Y-%m-%d")

        keyboard.append([
            InlineKeyboardButton(
                text=f"📅 {day.strftime('%d %b')}",
                callback_data=f"date|{formatted}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def generate_time_keyboard(selected_date: str):
    times = ["10:00","11:00","12:00","14:00","15:00","16:00","17:00","18:00"]
    booked = BOOKED_SLOTS.get(selected_date, {})
    keyboard = []
    now = tz_now()

    for time in times:
        booking_datetime = parse_booking_datetime(selected_date, time)

        if time not in booked and booking_datetime > now:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"⏰ {time}",
                    callback_data=f"time|{selected_date}|{time}"
                )
            ])

    keyboard.append([InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_dates")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_booking"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_booking")
            ]
        ]
    )

def admin_status_keyboard(booking_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Keldi", callback_data=f"came|{booking_id}"),
                InlineKeyboardButton(text="❌ Kelmagan", callback_data=f"notcame|{booking_id}")
            ]
        ]
    )


def admin_finish_keyboard(booking_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔧 Xizmatlarni tanlash", callback_data=f"finish|{booking_id}")
            ]
        ]
    )


def services_keyboard(booking_id: int, selected: list):
    keyboard = []

    for i, service in enumerate(SERVICES):
        mark = "✅ " if i in selected else ""
        keyboard.append([
            InlineKeyboardButton(
                text=f"{mark}🔧 {service['title']} — {service['price']} so‘m",
                callback_data=f"service|{booking_id}|{i}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="💰 Yakunlash", callback_data=f"complete|{booking_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# =========================
# XIZMATLARNI KO‘RISH
# =========================

@router.message(F.text == "🚗 Xizmatlarni ko‘rish")
async def show_services(message: types.Message):
    text = "🚗 <b>Servisimizdagi xizmatlar:</b>\n\n"

    for s in SERVICES:
        text += f"🔧 <b>{s['title']}</b>\n💰 Narxi: {s['price']} so‘m\n\n"

    await message.answer(text, parse_mode="HTML")


# =========================
# NAVBATGA YOZILISH
# =========================

@router.message(F.text == "📅 Navbatga yozilish")
async def booking_start(message: types.Message, state: FSMContext):
    await state.set_state(BookingState.choosing_date)

    await message.answer(
        "📅 <b>Quyidagi 15 kun ichidan qulay sanani tanlang:</b>",
        parse_mode="HTML",
        reply_markup=generate_dates_keyboard()
    )


@router.callback_query(F.data.startswith("date|"))
async def date_selected(callback: types.CallbackQuery, state: FSMContext):
    _, selected_date = callback.data.split("|")

    await state.update_data(date=selected_date)
    await state.set_state(BookingState.choosing_time)

    await callback.message.edit_text(
        f"⏰ <b>{selected_date}</b> sanasi uchun vaqtni tanlang:",
        parse_mode="HTML",
        reply_markup=generate_time_keyboard(selected_date)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("time|"))
async def time_selected(callback: types.CallbackQuery, state: FSMContext):
    _, selected_date, selected_time = callback.data.split("|")

    await state.update_data(time=selected_time)
    await state.set_state(BookingState.confirming)

    await callback.message.edit_text(
        f"📋 <b>Bron ma’lumotlari:</b>\n\n"
        f"📅 Sana: {selected_date}\n"
        f"⏰ Vaqt: {selected_time}\n\n"
        "Tasdiqlaysizmi?",
        parse_mode="HTML",
        reply_markup=confirm_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "confirm_booking")
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    global BOOKING_COUNTER

    data = await state.get_data()
    selected_date = data["date"]
    selected_time = data["time"]
    user_id = callback.from_user.id

    booking_datetime = datetime.datetime.strptime(
        f"{selected_date} {selected_time}", "%Y-%m-%d %H:%M"
    )

    booking_id = BOOKING_COUNTER
    BOOKING_COUNTER += 1

    BOOKINGS[booking_id] = {
        "user_id": user_id,
        "date": selected_date,
        "time": selected_time,
        "datetime": booking_datetime,
        "status": "⏳ Kutilmoqda",
        "services": []
    }

    BOOKED_SLOTS.setdefault(selected_date, {})[selected_time] = booking_id
    USER_BOOKINGS.setdefault(user_id, []).append(booking_id)

    await state.clear()

    await callback.message.edit_text(
        "✅ <b>Bron muvaffaqiyatli yaratildi!</b>\n\n"
        f"📅 {selected_date}\n"
        f"⏰ {selected_time}\n\n"
        "⏳ Belgilangan vaqtda servisga kelishingizni so‘raymiz.\n"
        "🚗 10 daqiqagacha kechikish mumkin.",
        parse_mode="HTML"
    )

    await bot.send_message(
        GROUP_ID,
        f"📥 <b>Yangi bron!</b>\n\n"
        f"🆔 ID: {booking_id}\n"
        f"📅 Sana: {selected_date}\n"
        f"⏰ Vaqt: {selected_time}",
        parse_mode="HTML",
        reply_markup=admin_status_keyboard(booking_id)
    )

    await callback.answer()


# =========================
# ADMIN STATUS NAZORATI
# =========================

@router.callback_query(F.data.startswith("came|"))
async def admin_came(callback: types.CallbackQuery):
    _, booking_id = callback.data.split("|")
    booking_id = int(booking_id)

    booking = BOOKINGS[booking_id]
    now = tz_now()

    # 10 minut oldin bosish mumkin
    if now < ensure_tz(booking["datetime"]) - datetime.timedelta(minutes=10):
        await callback.answer("🚫 Hali 10 daqiqa qolganidan oldin bosib bo‘lmaydi!", show_alert=True)
        return

    booking["status"] = "🚗 Keldi"

    await callback.message.edit_text(
        callback.message.text + "\n\n🚗 <b>Mijoz keldi</b>",
        parse_mode="HTML", reply_markup=admin_finish_keyboard(booking_id)
    )

    await callback.answer()
    

@router.callback_query(F.data.startswith("finish|"))
async def admin_finish(callback: types.CallbackQuery):
    _, booking_id = callback.data.split("|")
    booking_id = int(booking_id)

    await callback.message.edit_text(
        "🔧 Bajarilgan xizmatlarni tanlang:",
        reply_markup=services_keyboard(booking_id, BOOKINGS[booking_id]["services"])
    )

    await callback.answer()
    

@router.callback_query(F.data.startswith("service|"))
async def select_service(callback: types.CallbackQuery):
    _, booking_id, service_index = callback.data.split("|")
    booking_id = int(booking_id)
    service_index = int(service_index)

    selected = BOOKINGS[booking_id]["services"]

    if service_index in selected:
        selected.remove(service_index)
    else:
        selected.append(service_index)

    await callback.message.edit_reply_markup(
        reply_markup=services_keyboard(booking_id, selected)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("notcame|"))
async def admin_notcame(callback: types.CallbackQuery):
    _, booking_id = callback.data.split("|")
    booking_id = int(booking_id)

    booking = BOOKINGS[booking_id]
    now = tz_now()

    # 10 minut o‘tmaguncha bosib bo‘lmaydi
    if now < ensure_tz(booking["datetime"]) + datetime.timedelta(minutes=10):
        await callback.answer("⏳ 10 daqiqa o‘tishini kuting!", show_alert=True)
        return

    booking["status"] = "❌ Kelmadi"

    await callback.message.edit_text(
        callback.message.text + "\n\n❌ <b>Mijoz kelmadi</b>",
        parse_mode="HTML"
    )

    await callback.answer()
    

@router.callback_query(F.data.startswith("complete|"))
async def complete_booking(callback: types.CallbackQuery, bot: Bot):
    _, booking_id = callback.data.split("|")
    booking_id = int(booking_id)

    booking = BOOKINGS[booking_id]
    total = sum(SERVICES[i]["price"] for i in booking["services"])

    booking["status"] = "Yakunlandi"
    booking["total"] = total

    COMPLETED_BOOKINGS.append(booking_id)

    text = (
        f"✅ <b>Buyurtma yakunlandi</b>\n\n"
        f"📅 {booking['date']}\n"
        f"⏰ {booking['time']}\n"
        f"💰 Jami: {total} so‘m\n\n"
        "Servisimizdan foydalanganingiz uchun rahmat!"
    )

    await bot.send_message(booking["user_id"], text, parse_mode="HTML")

    await callback.message.edit_text(
        f"<b>Muvaffaqiyatli yakunlandi ✅</b>\n\n🆔 ID: {booking_id}\n💰 Jami: {total} so‘m\n✅ Status: Yakunlandi"
    )

    await callback.answer()


# =========================
# MENING BUYURTMALARIM
# =========================

@router.message(F.text == "🛠 Mening buyurtmalarim")
async def my_bookings(message: types.Message):
    user_id = message.from_user.id
    ids = USER_BOOKINGS.get(user_id)

    if not ids:
        await message.answer("📭 Sizda hali hech qanday bron mavjud emas.")
        return

    text = "📋 <b>Sizning bronlaringiz:</b>\n\n"

    for i in ids:
        b = BOOKINGS[i]
        text += (
            f"🆔 ID: {i}\n"
            f"📅 {b['date']} | ⏰ {b['time']}\n"
            f"📌 Holat: {b['status']}\n\n"
        )

    await message.answer(text, parse_mode="HTML")


# =========================
# LOKATSIYA
# =========================

@router.message(F.text == "📍 Lokatsiya")
async def location_handler(message: types.Message):
    await message.answer_location(
        latitude=41.321758,
        longitude=69.202432
    )
    await message.answer("📍 Bizning servis manzilimiz yuqorida ko‘rsatilgan.")


# =========================
# KONTAKT
# =========================

@router.message(F.text == "📞 Kontakt")
async def contact_handler(message: types.Message):
    await message.answer(
        "📞 <b>Bog‘lanish uchun:</b>\n\n"
        "📱 Telefon: +998 97 773 88 85\n"
        "🕘 Ish vaqti: 09:00 - 20:00\n\n"
        "🚗 Sizni kutib qolamiz!",
        parse_mode="HTML"
    )


# =========================
# MUROJAAT
# =========================

@router.message(F.text == "💬 Murojaat yuborish")
async def start_contact(message: types.Message, state: FSMContext):
    await state.set_state(ContactState.waiting_message)

    await message.answer(
        "💬 <b>Murojaatingizni yozib qoldiring.</b>\n\n"
        "✍️ Xabaringizni yuboring:",
        parse_mode="HTML"
    )


@router.message(ContactState.waiting_message)
async def receive_contact(message: types.Message, state: FSMContext, bot: Bot):
    await bot.send_message(
        GROUP_ID,
        f"💬 <b>Yangi murojaat:</b>\n\n"
        f"👤 @{message.from_user.username}\n"
        f"📝 {message.text}",
        parse_mode="HTML"
    )

    await message.answer("✅ Murojaatingiz yuborildi. Tez orada javob beramiz.")
    await state.clear()
