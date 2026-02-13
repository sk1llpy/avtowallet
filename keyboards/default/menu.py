from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def button():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🚗 Xizmatlarni ko‘rish")
            ],
            [
                KeyboardButton(text="📅 Navbatga yozilish"),
                KeyboardButton(text="🛠 Mening buyurtmalarim")
            ],
            [
                KeyboardButton(text="📍 Lokatsiya"),
                KeyboardButton(text="📞 Kontakt")
            ],
            [
                KeyboardButton(text="💬 Murojaat yuborish")
            ]
        ],
        resize_keyboard=True
    )
