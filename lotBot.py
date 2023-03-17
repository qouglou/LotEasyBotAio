import asyncio

from aiogram import Bot, Dispatcher, F
import conf
import logging
from handlers import user_handlers, admin_handlers, start_rules_handlers
from middlewares.ban_rules_check import BanRulesCallbackMiddleware

from db import BotDB
from aiogram.fsm.storage.memory import MemoryStorage
from checkers import Checkers as ch

db = BotDB('lotEasy.db')
logging.basicConfig(
    level=logging.WARNING,
    filename="difs/logs.log",
    format="%(asctime)s %(levelname)s %(funcName)s %(message)s")
logging.info("Bot successfully started!")


async def main():
    bot = Bot(token=conf.TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(start_rules_handlers.router, user_handlers.router, admin_handlers.router)
    dp.callback_query.outer_middleware(BanRulesCallbackMiddleware())
    dp.message.filter(F.chat.type == "private")
    if conf.ch_start:
        asyncio.gather(ch().topup_cheker_all(), ch().winner_warned_checker())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
