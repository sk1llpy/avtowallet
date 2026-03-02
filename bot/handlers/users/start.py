# bot/handlers/users/start.py
from __future__ import annotations

from aiogram import F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from sqlalchemy.orm import Session

from bot.decorators import create_session
from bot.routers import users as router

from db.repository import UsersRepository, EmployeesRepository

# ✅ siz aytgan keyboardlar
from bot.keyboards.default import menu as menu_kb
from bot.keyboards.default import contact as contact_kb


# =========================
# STATES
# =========================
class RegisterState(StatesGroup):
    phone = State()
    full_name = State()


# =========================
# HELPERS
# =========================
def split_name(text: str) -> tuple[str | None, str | None]:
    """
    "Abdulloh Nugmonov" -> ("Abdulloh", "Nugmonov")
    "Abdulloh" -> ("Abdulloh", None)
    "Abdulloh Nuriddin o'g'li Nugmonov" -> ("Abdulloh", "Nugmonov")
    """
    raw = (text or "").strip()
    if not raw:
        return None, None

    parts = [p for p in raw.split() if p.strip()]
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[-1]


def user_is_fully_registered(user) -> bool:
    if not user:
        return False
    if not getattr(user, "phone_number", None):
        return False
    if getattr(user, "first_name", None) or getattr(user, "tg_full_name", None):
        return True
    return False


def employee_menu_kb() -> ReplyKeyboardMarkup:
    """
    Employee uchun maxsus menyu (Reply keyboard).
    Siz xohlasangiz keyin buni alohida filega ko'chiramiz.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Oyliklarim"), KeyboardButton(text="✅ Bajarilgan bronlar")],
            [KeyboardButton(text="📅 Bugungi bronlar"), KeyboardButton(text="🧾 Mening ishlarim")],
            [KeyboardButton(text="👤 Profil"), KeyboardButton(text="🏠 Asosiy")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True,
    )


async def send_user_menu(message: Message, *, is_employee: bool):
    """
    Ro'yxatdan o'tgandan keyin yoki /start bosilganda menyu yuboradi.
    - oddiy user => menu_kb.button()
    - employee => employee_menu_kb()
    """
    if is_employee:
        await message.answer(
            "👷‍♂️ <b>Xodim paneli</b>\n\n"
            "Quyidagi menyudan kerakli bo‘limni tanlang 👇",
            reply_markup=employee_menu_kb(),
            parse_mode="HTML",
        )
        return

    # oddiy user uchun sizning tayyor menu keyboard
    kb = await menu_kb.button()
    await message.answer(
        "🏠 <b>Asosiy menyu</b>\n\n"
        "Xizmatlardan foydalanish uchun menyudan tanlang 👇",
        reply_markup=kb,
        parse_mode="HTML",
    )


# =========================
# START / REGISTER FLOW
# =========================
@router.message(CommandStart())
@create_session
async def start_cmd(message: Message, state: FSMContext, session: Session):
    tg_id = str(message.from_user.id)

    user = UsersRepository.get("tg_id", tg_id, session)

    # employee tekshirish (user bo‘lmasa ham keyin yaratamiz)
    is_employee = False
    if user:
        emp = EmployeesRepository.get("user_id", user.id, session)
        is_employee = bool(emp)

    # Agar user to'liq ro'yxatdan o'tgan bo'lsa => darrov menu
    if user_is_fully_registered(user):
        await state.clear()
        await message.answer(
            "✅ <b>Xush kelibsiz!</b> 😊",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="HTML",
        )
        await send_user_menu(message, is_employee=is_employee)
        return

    # Aks holda ro'yxatdan o'tkazamiz
    await state.clear()
    await state.set_state(RegisterState.phone)

    # kontakt so‘rash uchun sizning contact keyboard
    kb = await contact_kb.button()
    await message.answer(
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "📝 <b>Ro‘yxatdan o‘tish</b> uchun telefon raqamingizni yuboring.\n\n"
        "📌 Pastdagi tugmani bosing: <i>Telefon raqamni yuborish</i>",
        reply_markup=kb,
        parse_mode="HTML",
    )


# =========================
# STEP 1: PHONE
# =========================
@router.message(RegisterState.phone, F.contact)
@create_session
async def register_phone(message: Message, state: FSMContext, session: Session):
    contact = message.contact
    if not contact:
        await message.answer("❌ Telefon raqam topilmadi. Qaytadan yuboring.", parse_mode="HTML")
        return

    # faqat o'zining kontaktini qabul qilamiz
    if message.from_user and contact.user_id and contact.user_id != message.from_user.id:
        await message.answer(
            "❌ <b>Iltimos</b>, faqat <b>o‘zingizning</b> telefon raqamingizni yuboring.",
            parse_mode="HTML",
        )
        return

    phone = (contact.phone_number or "").strip()
    if not phone:
        await message.answer("❌ Telefon raqam topilmadi. Qaytadan yuboring.", parse_mode="HTML")
        return

    phone = f"+{phone}" if not phone.startswith("+") else phone

    await state.update_data(phone_number=phone)
    await state.set_state(RegisterState.full_name)

    await message.answer(
        "✅ <b>Rahmat!</b> 📞\n\n"
        "Endi <b>ismingiz</b> (va xohlasangiz <b>familiyangiz</b>)ni yozing:\n"
        "🧾 Masalan: <i>Abdulloh Nugmonov</i>\n\n"
        "⚪ Familiya ixtiyoriy: <i>Abdulloh</i> deb yozsangiz ham bo‘ladi.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )


@router.message(RegisterState.phone)
async def register_phone_wrong(message: Message, state: FSMContext):
    kb = await contact_kb.button()
    await message.answer(
        "📞 Iltimos, telefon raqamingizni <b>tugma orqali</b> yuboring 👇",
        reply_markup=kb,
        parse_mode="HTML",
    )


# =========================
# STEP 2: FULL NAME
# =========================
@router.message(RegisterState.full_name, F.text)
@create_session
async def register_full_name(message: Message, state: FSMContext, session: Session):
    data = await state.get_data()
    phone = (data.get("phone_number") or "").strip()

    if not phone or phone == "+":
        await state.clear()
        await state.set_state(RegisterState.phone)
        kb = await contact_kb.button()
        await message.answer(
            "⚠️ <b>Qaytadan boshlaymiz.</b>\n\nTelefon raqamingizni yuboring:",
            reply_markup=kb,
            parse_mode="HTML",
        )
        return

    first_name, last_name = split_name(message.text)
    if not first_name:
        await message.answer(
            "❌ Ismni to‘g‘ri kiriting.\n\n"
            "Masalan: <i>Abdulloh</i> yoki <i>Abdulloh Nugmonov</i>",
            parse_mode="HTML",
        )
        return

    tg_id = str(message.from_user.id)
    tg_username = message.from_user.username
    tg_full_name = (message.text or "").strip()

    # bor bo'lsa update, bo'lmasa create
    user = UsersRepository.get("tg_id", tg_id, session)
    if user:
        UsersRepository.edit(
            conditions={"id": user.id},
            edits={
                "phone_number": phone,
                "first_name": first_name,
                "last_name": last_name,
                "tg_username": tg_username,
                "tg_full_name": tg_full_name,
            },
            session=session,
        )
        # qaytadan olish (employee check uchun)
        user = UsersRepository.get("id", user.id, session)
    else:
        user = UsersRepository.create(
            params={
                "tg_id": tg_id,
                "tg_username": tg_username,
                "tg_full_name": tg_full_name,
                "first_name": first_name,
                "last_name": last_name,
                "phone_number": phone,
            },
            session=session,
        )

    # employee check
    emp = EmployeesRepository.get("user_id", user.id, session)
    is_employee = bool(emp)

    await state.clear()
    await message.answer(
        "🎉 <b>Muvaffaqiyatli ro‘yxatdan o‘tdingiz!</b> ✅\n\n"
        "Endi menyudan foydalanishingiz mumkin 👇",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )

    await send_user_menu(message, is_employee=is_employee)


@router.message(RegisterState.full_name)
async def register_full_name_wrong(message: Message):
    await message.answer(
        "✍️ Iltimos, ismingizni yozing.\n"
        "Masalan: <i>Abdulloh</i> yoki <i>Abdulloh Nugmonov</i>",
        parse_mode="HTML",
    )