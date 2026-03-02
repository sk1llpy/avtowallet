from bot.misc import dp, bot
from bot.utils import logging, include_routers
from bot import handlers


async def polling():
    await include_routers.include_routers()
    
    await dp.start_polling(bot)