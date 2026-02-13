from misc import dp, bot
from utils import logging, include_routers

import handlers

async def polling():
    await include_routers.include_routers()
    
    await dp.start_polling(bot)