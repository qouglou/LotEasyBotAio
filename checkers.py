import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import conf
from db import BotDB as database
from buttonsTg import ButtonsTg as b
bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot)
db = database('lotEasy.db')


class Checkers:

    async def topupChekerAll(self):
        print("Checking users topups is enabled")
        while True:
            print(f"Lines not done topups - {await db.get_lines_no_topup()}")
            M = 0
            while M < int(await db.get_lines_no_topup()):
                int_pay, user_id, sum, accrued, done = await db.all_no_topup_checker(M)
                if accrued and done is False:
                    await db.topup_balance(user_id, sum)
                    await db.set_topup_done(int_pay)
                    m_success_topup = (f"\U00002705 *Пополнение №{int_pay} успешно выполнено!*"
                                       f"\n\n*Ваш баланс:*\n{int(await db.get_user_balance(user_id))}₽")
                    await bot.send_message(user_id, m_success_topup, "Markdown",
                                           reply_markup=types.InlineKeyboardMarkup(1).add(await b().button_lk()))
                M += 1
            await asyncio.sleep(10)

    async def data_checker(self, mfu):
        if (await db.get_user_name(mfu.id) != mfu.first_name) or (
                await db.get_user_lastname(mfu.id) != mfu.last_name) or (
                await db.get_user_username(mfu.id) != mfu.username):
            await db.update_data(mfu.first_name, mfu.last_name, mfu.username,
                                 mfu.id)

    async def rules_checker(self, user_id):
        if not await db.get_rules_accept(user_id):
            await b().ButtonRulesAccept(user_id, False)
        elif await db.get_ban(user_id):
            await b().ButtonBan(user_id)
        return await db.get_rules_accept(user_id), await db.get_ban(user_id)

    async def winnerWarnedChecker(self):
        print("Checking the notifications of the winners")
        while True:
            count_lines = await db.get_lines_no_warned()
            M = 0
            print(f"Lines not warned winners - {count_lines}")
            while M < count_lines:
                id_game, num_win, warned, game = [await db.all_no_warned_checker(M)]
                if game == "Дуэль":
                    g_line = "duel"
                elif game == "Русская рулетка":
                    g_line = "russ"
                elif game == "Королевская битва":
                    g_line = "king"
                if (num_win != 0) and (warned is False):
                    user_id, bet = [await db.get_winner(id_game, g_line, num_win)]
                    line = f"\U0001F389 *Вы победили в игре *\n{game} №{id_game}"\
                           f"\nВаш выигрыш - *{bet}₽*\nПроверьте свою удачу еще раз!\n"
                    await db.topup_balance(user_id, bet)
                    await db.warned_winner(g_line, id_game)
                    key_again = types.InlineKeyboardButton(text='\U0000267B Попробовать еще раз',
                                                           callback_data='change_bet')
                    await bot.send_message(user_id, line, "Markdown",
                                           reply_markup=types.InlineKeyboardMarkup(1).add(key_again, await b().button_lk()))
                M += 1
            await asyncio.sleep(10)






