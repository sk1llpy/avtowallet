import datetime

from aiogram import types, html, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from routers import users as router
from keyboards.default import menu, contact
from states.register import RegisterState

USERS = {}


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if USERS.get(user_id):
        await message.answer(
            text=html.bold(
                "👋 Assalomu alaykum!\n\n"
                "Siz allaqachon ro'yxatdan o'tgansiz ✅\n"
                "Botimizdan bemalol foydalanishingiz mumkin 🚀"
            ),
            reply_markup=await menu.button()
        )
    else:
        await state.set_state(RegisterState.phone_number)
        await message.answer(
            text=html.bold(
                "👋 Assalomu alaykum!\n\n"
                "Botimizga xush kelibsiz 🤖\n"
                "Davom etish uchun telefon raqamingizni yuboring 📱"
            ),
            reply_markup=await contact.button()
        )


@router.message(
    F.content_type == types.ContentType.CONTACT,
    StateFilter(RegisterState.phone_number)
)
async def get_contact(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    phone = message.contact.phone_number if message.contact.phone_number.startswith("+") else f"+{message.contact.phone_number}"

    if message.contact.user_id != user_id:
        await message.answer(
            "❗ Iltimos, o'zingizning telefon raqamingizni yuboring.",
            reply_markup=await contact.button()
        )
        return

    USERS[user_id] = {
        "phone_number": phone,
        "created_at": datetime.datetime.now()
    }

    await state.clear()

    await message.answer(
        text=html.bold(
            "🎉 Tabriklaymiz!\n\n"
            "Siz muvaffaqiyatli ro'yxatdan o'tdingiz ✅\n"
            f"📱 Telefon raqamingiz: {phone}\n\n"
            "Endi botdan to'liq foydalanishingiz mumkin 🚀"
        ),
        reply_markup=await menu.button()
    )
