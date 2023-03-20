from aiogram import types, Router, F
from aiogram.filters.command import Command
from middlewares.ban_rules_check import BanMsgMiddleware
from templates.texts import TextsTg as t
from templates.buttons import ButtonsTg as b
from checkers import Checkers as ch
from templates.messages import Messages as msg
from db_conn_create import db
from configs.logs_config import logs

router = Router()
router.message.middleware(BanMsgMiddleware())


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    if not await db.get_user_exists(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name,
                          message.from_user.last_name, message.from_user.username)
        logs.info(f"User {message.from_user.id} start to use Bot with message {message}")
        await msg().rules_accept(message, True)
    await ch().data_checker(message.from_user)
    if await db.get_rules_accept(message.from_user.id) == 0:
        await msg().rules_accept(message, False)
    else:
        await msg().not_new(message)


@router.message(F.text == "\U0001F4D5 Правила")
async def main_new_rules(message):
    await message.delete()
    await message.answer(t.m_rules)


@router.message(F.text == "\U00002705 Принять правила")
async def main_start(message):
    await message.answer("<b>Теперь вы можете воспользоваться нашим ботом</b>", reply_markup=await b().KB_Start())
    await db.set_rules_accept(message.from_user.id)
    logs.info(f"User {message.from_user.id} accept rules")