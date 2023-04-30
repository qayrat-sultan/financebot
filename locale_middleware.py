from typing import Tuple, Any

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware

from config import I18N_DOMAIN, LOCALES_DIR, redis

STANDING_USER = ":1"
FIRST_TIME_USER = ":0"


async def get_lang(user_id):
    # await redis.set()
    value = await redis.get(user_id)
    if not value:
        # TODO: get API language
        value = "en" + FIRST_TIME_USER
        await redis.set(user_id, value)

    return value.split(":")[0]


class APILanguageMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):
        user = types.User.get_current()
        locale = await get_lang(user.id)
        return locale or user.locale


i18n = APILanguageMiddleware(I18N_DOMAIN, LOCALES_DIR)
