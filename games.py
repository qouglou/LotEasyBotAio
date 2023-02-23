import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import conf
import random
from texts import TextsTg as t
from db import BotDB as db

bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot)


db = db('lotEasy.db')


async def get_offline_values(game, dice_value):
    coef = 0
    txt = "*К сожалению, вы ничего не выиграли\n\nПопробуйте еще раз!*"
    if game == "bowl":
        if dice_value == 6:
            coef = conf.bowl_strike
            txt = "*Страйк! \U0001F389\U0001F911\nПоздравляем!*\n\n"
        elif dice_value == 5:
            coef = conf.bowl_hit_5
            txt = "*5 сбитых - отличный результат!*\n\n"
        elif dice_value == 4:
            coef = conf.bowl_hit_4
            txt = "*4 сбитых - неплохой результат*\n\n"
        elif dice_value == 3:
            coef = conf.bowl_hit_3
            txt = "*Половина сбита - ни туда, ни сюда*\n\n"
    elif game == "cube":
        if dice_value == 6:
            coef = conf.dice_6
            txt = "*6 очков! Отлично! \U0001F389\U0001F911\nПоздравляем!*\n\n"
        elif dice_value == 5:
            coef = conf.dice_5
            txt = "*5 очков - отличный результат!*\n\n"
        elif dice_value == 4:
            coef = conf.dice_4
            txt = "*На кубике 4 - неплохой результат*\n\n"
        elif dice_value == 3:
            coef = conf.bowl_hit_3
            txt = "*3 точки - ни туда, ни сюда*\n\n"
    elif game == "slot":
        if dice_value == 64:
            coef = conf.slot_jackpot
            txt = "*Джекпот! \U0001F389\U0001F911\nУдача явно на вашей стороне!*\n\n"
        elif dice_value in (1, 22, 43):
            coef = conf.slot_other_3
            txt = "*3 в ряд! Вот это удача! \U0001F389\U0001F911\nПоздравляем!*\n\n"
        elif dice_value in (16, 32, 48, 52, 56, 60, 61, 62, 63):
            coef = conf.slot_7_2
            txt = "*Две семерки - тоже победа! \U0001F389\nПоздравляем!*\n\n"
        elif dice_value in (4, 13, 24, 30, 44, 47, 49, 54, 59):
            coef = conf.slot_7_1
            txt = "*Одна семерка и два в ряд - неплохо! \U0001F389\nПоздравляем!*\n\n"
        elif dice_value in (7, 8, 10, 12, 14, 15, 19, 20, 25, 28, 29, 31, 34, 36, 37, 40, 45, 46, 50, 51, 53, 55, 57, 58):
            coef = conf.slot_diff
            txt = "*Выбить все разное - тоже надо постараться!*\n\n"
    return coef, txt