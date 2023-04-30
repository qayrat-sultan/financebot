from aiogram import Dispatcher

from config import redis


async def on_startup(dp: Dispatcher):
    ...


async def on_shutdown(dp: Dispatcher):
    print("Closing connections")
    await redis.close()
