from aiogram import Router, Dispatcher

from misc import dp
from utils.helpful_functions import router
from routers import (users, groups, channels, admins)


async def include_routers():
    return (
        await router(dispatcher = dp, router = users),
        await router(dispatcher = dp, router = groups),
        await router(dispatcher = dp, router = admins),
        await router(dispatcher = dp, router = channels)
    )