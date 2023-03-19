import asyncio

from aiogram import Bot, Dispatcher, F
from bot.configs import conf
from bot.configs.logs_config import logs
from bot.handlers import bot_blocked_handlers, admin_handlers, start_rules_handlers, user_handlers
from bot.middlewares.ban_rules_check import BanRulesCallbackMiddleware
from bot.middlewares.bot_blocked_check import BotBlockedCallMiddleware, BotBlockedMsgMiddleware
from aiogram.fsm.strategy import FSMStrategy
from aiogram.fsm.storage.memory import MemoryStorage
from bot.checkers import Checkers as ch
from bot.configs.env_reader import env_config

logs.warning("Bot successfully started!")


async def main():
    bot = Bot(token=env_config.bot_token.get_secret_value(), parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)
    dp.include_routers(bot_blocked_handlers.router, start_rules_handlers.router, user_handlers.router, admin_handlers.router)
    dp.callback_query.outer_middleware(BanRulesCallbackMiddleware())
    dp.callback_query.outer_middleware(BotBlockedCallMiddleware())
    dp.message.outer_middleware(BotBlockedMsgMiddleware())
    dp.my_chat_member.filter(F.chat.type == "private")
    dp.message.filter(F.chat.type == "private")
    if conf.ch_start:
        asyncio.gather(ch().topup_cheker_all(bot), ch().winner_warned_checker(bot))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
