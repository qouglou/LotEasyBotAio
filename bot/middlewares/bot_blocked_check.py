from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from bot.db_conn_create import db


def _is_bot_blocked(user_id):
    return db.get_bot_block(user_id)


class BotBlockedCallMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        call: CallbackQuery,
        data: Dict[str, Any]
    ):
        if not await _is_bot_blocked(call.from_user.id):
            return await handler(call, data)


class BotBlockedMsgMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ):
        if not await _is_bot_blocked(message.from_user.id):
            return await handler(message, data)
