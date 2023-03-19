from aiogram import Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated
from bot.db_conn_create import db
from bot.configs.logs_config import logs

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_bot_block(event: ChatMemberUpdated):
    await db.set_user_block_bot(event.from_user.id, True)
    logs.info(f"User {event.from_user.id} block bot")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_bot_unblock(event: ChatMemberUpdated):
    await db.set_user_block_bot(event.from_user.id, False)
    logs.info(f"User {event.from_user.id} unblock bot")