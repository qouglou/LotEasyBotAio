import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import conf
from db import BotDB as database
from buttons import ButtonsTg as b
bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot)
db = database('lotEasy.db')


class Messages:

    async def rules_accept(self, user_id, newbie):
        if newbie:
            text_send = f"Данный бот поможет вам быстро потерять свои деньги. \U0001F4B8\n" \
                        f"\nНажимая кнопку *Принять правила* вы принимаете правила его использования и подтверждаете " \
                        f"свое совершеннолетие. \U0001F51E"
        else:
            text_send = "Вы не можете пользоваться данным ботом, пока не приняли правила."
        await bot.send_message(user_id, text_send, parse_mode="Markdown",
                               reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
                                   "\U00002705 Принять правила", "\U0001F4D5 Правила"))

    async def no_access(self, adm_id, need_lvl, msg_id=False):
        keyboard = types.InlineKeyboardMarkup().add(await b().BT_adm_lk())
        if msg_id:
            await bot.edit_message_text(f"*Недостаточно прав. \n\nНеобходимо иметь уровень {need_lvl} и выше.*",
                                          adm_id, msg_id, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await bot.send_message(adm_id, f"*Недостаточно прав.\n\nНеобходимо иметь уровень {need_lvl} и выше.*",
                reply_markup=keyboard, parse_mode="Markdown")

    async def bpmanag_no(self, user_id):
        await bot.send_message(user_id, "Нет доступа", reply_markup=types.InlineKeyboardMarkup().add(
            await self.BT_close()), parse_mode="Markdown")

    async def adm_no_valid(self, user_id, ex_adm, msg_id=0):
        keyboard = types.InlineKeyboardMarkup().add(await b().BT_support())
        if ex_adm:
            await bot.edit_message_text("*Нет доступа.* \n\nЕсли это ошибка, вы можете связаться с главным админом",
                                        user_id, msg_id, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await bot.send_message(user_id, "*Нет доступа.* \n\nЕсли это ошибка, вы можете связаться с главным админом",
                                   reply_markup=keyboard, parse_mode="Markdown")

    async def not_new(self, user_id):
        await bot.send_message(user_id, "\U0001F450 Рады видеть вас снова!",
                               reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   types.KeyboardButton("\U00002139 Меню")))