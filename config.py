import logging
import aioredis
from pathlib import Path

from environs import Env
from aiogram.contrib.fsm_storage.redis import RedisStorage

# environs kutubxonasidan foydalanish
env = Env()
env.read_env()
DEBUG = env.bool("DEBUG", True)
# .env fayl ichidan quyidagilarni o'qiymiz
BOT_TOKEN = env.str("BOT_TOKEN")  # Bot toekn
ADMINS = env.list("ADMINS", "19353535")  # adminlar ro'yxati
API_URL = env("API_URL", "https://financeapi.itlink.uz/api/")
MAIN_URL = env("MAIN_URL", "https://financeapi.itlink.uz/")
API_TOKEN = env("API_TOKEN", None)

I18N_DOMAIN = 'mybot'
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / 'locales'


# create a Redis client
redis = aioredis.from_url('redis://localhost:6379', decode_responses=True)

if DEBUG is False:
    try:
        import sentry_sdk
        SENTRY_DSN = env.str("SENTRY_DSN")
        sentry_sdk.init(
            dsn=SENTRY_DSN,

            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            # We recommend adjusting this value in production.
            traces_sample_rate=1.0
        )
    except ModuleNotFoundError:
        logging.warning("Please if you use DEBUG mode change .env file environ varialbe DEBUG=False to Debug=True "
                        "or delete variable line!")
