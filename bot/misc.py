from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from data.config import BotSettings

bot_settings = BotSettings()
storage = MemoryStorage()
dp = Dispatcher(
    storage = storage
)
bot = Bot(
    token = bot_settings.token,
    default = DefaultBotProperties(
        parse_mode = ParseMode.HTML
    )
)