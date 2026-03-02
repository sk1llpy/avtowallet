from aiogram import Router, Dispatcher

async def router(dispatcher: Dispatcher | Router, router: Router) -> Dispatcher | Router:
    return dispatcher.include_router(router = router)