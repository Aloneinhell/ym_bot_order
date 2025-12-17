import asyncio
import logging
import os

import dotenv
from aiogram import Dispatcher

from data import database

from config import bot
from handlers import get_full_router

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from services.utils.get_api_creds import get_api_keys
from services.ym.ym_checker_sender import YmCheckerSender

dotenv.load_dotenv()
bot = bot
dp = Dispatcher()
logger = logging.getLogger(__name__)

dev = 'xeeliq'


async def main():
    await database.init_db()
    logging.basicConfig(level=logging.DEBUG)
    dp.include_router(get_full_router())

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    api_keys = await get_api_keys()
    if api_keys:
        ym_checker_sender = YmCheckerSender(api_keys=api_keys)

        scheduler.add_job(ym_checker_sender.check_and_send, 'interval', seconds=10)

        scheduler.start()

    await dp.start_polling(bot)
    await bot.get_my_description()



if __name__ == '__main__':
    asyncio.run(main())
