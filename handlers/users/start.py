import datetime

from aiogram import types, html, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from zoneinfo import ZoneInfo

from routers import users as router
from keyboards.default import menu, contact
from states.register import RegisterState
from misc import bot
from . import menu

USERS = {}
TASHKENT_TZ = ZoneInfo("Asia/Tashkent")


class AnswerState(StatesGroup):
    waiting_message = State()


@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    spltd = message.text.split()
    
    if len(spltd) == 1:
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
    else:
        if spltd[1] and spltd[1].startswith("answer__"):
            question_id = spltd[1].split("__")[-1]
            
            await state.set_state(AnswerState.waiting_message)
            await state.update_data(question_id=question_id)

            await message.answer(
                text=html.bold("Javob yozing ✍️")
            )


@router.message(F.content_type == types.ContentType.TEXT, StateFilter(AnswerState.waiting_message))
async def answer_message_handler(message: types.Message, state: FSMContext):
    answer = message.text
    
    data = await state.get_data()
    question_id = data.get("question_id")
    
    try:
        await bot.send_message(chat_id=question_id, text=f"""<b>Sizga admin tomonidan javob yuborildi ✅</b>

    <i>✍️ {answer}</i>""")
    except:
        pass
    
    await state.clear()
    await message.answer(text=html.bold(f"Javob muvvafaqiyatli yuborildi ✅"))
    


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
        "created_at": datetime.datetime.now(TASHKENT_TZ)
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
