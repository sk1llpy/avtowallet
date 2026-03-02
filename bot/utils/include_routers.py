from aiogram import Router, Dispatcher

from bot.misc import dp
from bot.utils.helpful_functions import router
from bot.routers import (users, groups, channels, admins)


async def include_routers():
    return (
        await router(dispatcher = dp, router = users),
        await router(dispatcher = dp, router = groups),
        await router(dispatcher = dp, router = admins),
        await router(dispatcher = dp, router = channels)
    )