from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from bot.templates.messages import Messages as msg
from bot.db_conn_create import db


def _is_user_banned(user_id):
    return db.get_ban(user_id)


def _is_rules_accepted(user_id):
    return db.get_rules_accept(user_id)


class BanRulesCallbackMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        call: CallbackQuery,
        data: Dict[str, Any]
    ):
        if not await _is_user_banned(call.from_user.id):
            if await _is_rules_accepted(call.from_user.id):
                return await handler(call, data)
            else:
                await msg().rules_accept(call.message, False)
        else:
            await msg().info_ban(call.message)
        return


class BanRulesMsgMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ):
        if not await _is_user_banned(message.from_user.id):
            if await _is_rules_accepted(message.from_user.id):
                return await handler(message, data)
            else:
                await msg().rules_accept(message, False)
        else:
            await msg().info_ban(message)
        return


class BanMsgMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ):
        if not await _is_user_banned(message.from_user.id):
            return await handler(message, data)
        else:
            await msg().info_ban(message)
        return