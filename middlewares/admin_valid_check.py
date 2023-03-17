from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from messages import Messages as msg
from aiogram.types import Message, CallbackQuery
from db import BotDB
db = BotDB('lotEasy.db')


def _is_admin_valid(user_id):
    return db.adm_valid_check(user_id)


def _is_user_admin(user_id):
    return db.adm_check(user_id)


class AdminValidCallMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        call: CallbackQuery,
        data: Dict[str, Any]
    ):
        if await _is_user_admin(call.from_user.id):
            if await _is_admin_valid(call.from_user.id):
                return await handler(call, data)
            else:
                return await msg().adm_no_valid(call, "call")
        else:
            return await msg().bpmanag_no(call, "call")


class AdminValidMsgMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ):
        if await _is_user_admin(message.from_user.id):
            if await _is_admin_valid(message.from_user.id):
                return await handler(message, data)
            else:
                return await msg().adm_no_valid(message, "message")
        else:
            return await msg().bpmanag_no(message, "message")