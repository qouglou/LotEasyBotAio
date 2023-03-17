import asyncio

from aiogram import Bot, types, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import conf
from buttons import ButtonsTg as b
dp = Dispatcher(storage=MemoryStorage())


class Messages:

    async def rules_accept(self, message, newbie):
        if newbie:
            text_send = f"Данный бот поможет вам быстро потерять свои деньги. \U0001F4B8\n" \
                        f"\nНажимая кнопку <b>Принять правила</b> вы принимаете правила его использования и подтверждаете " \
                        f"свое совершеннолетие. \U0001F51E"
        else:
            text_send = "<b>Вы не можете пользоваться данным ботом, пока не приняли правила</b>"
        await message.answer(text=text_send,
                               reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
                                   [types.KeyboardButton(text="\U00002705 Принять правила")],
                                   [types.KeyboardButton(text="\U0001F4D5 Правила")]
                               ]))

    async def no_access(self, object, need_lvl, type):
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[await b().BT_AdmLk()])
        if type == "call":
            await object.message.edit_text(text=f"<b>Недостаточно прав. \n\nНеобходимо иметь уровень {need_lvl} и выше.</b>",
                                           reply_markup=keyboard)
        else:
            await object.answer(text=f"<b>Недостаточно прав.\n\nНеобходимо иметь уровень {need_lvl} и выше.</b>",
                reply_markup=keyboard)

    async def bpmanag_no(self, object, type):
        if type == "call":
            await object.message.edit_text(text="Нет доступа",
                                   reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[await b().BT_Close()]))
        else:
            await object.answer(text="Нет доступа",
                                       reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[await b().BT_Close()]]))

    async def adm_no_valid(self, object, type):
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[await b().BT_Support()]])
        if type == "call":
            await object.message.edit_text(text="<b>Нет доступа.</b> \n\nЕсли это ошибка, вы можете связаться с главным админом",
                                        reply_markup=keyboard)
        else:
            await object.answer(text="<b>Нет доступа.</b> \n\nЕсли это ошибка, вы можете связаться с главным админом",
                                   reply_markup=keyboard)

    async def not_new(self, message):
        await message.answer(text=f"\U0001F450 Рады видеть вас снова!",
                               reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[types.KeyboardButton(text="\U00002139 Меню")]]))

    async def info_ban(self, message):
        await message.answer(text="<b>Вы заблокированы \n\nДля возможного снятия блокировки вы можете связаться с поддержкой</b>",
                               reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[await b().BT_Support()]]))