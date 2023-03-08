import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import conf
import games
import logging
from db import BotDB as database
from buttons import ButtonsTg as b
bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot)
db = database('lotEasy.db')
logging.basicConfig(
    level=logging.WARNING,
    filename="difs/logs.log",
    filemode="a",
    format="%(asctime)s %(levelname)s %(funcName)s %(message)s")


class Checkers:

    async def topup_cheker_all(self):
        logging.warning(f"Topup checker is successfully  started")
        while True:
            logging.warning(f"Lines not done topups - {await db.get_lines_no_topup()}")
            M = 0
            while M < int(await db.get_lines_no_topup()):
                int_pay, user_id, sum, accrued, done = await db.all_no_topup_checker()
                if accrued and done is False:
                    await db.set_topup_balance(user_id, sum)
                    await db.set_topup_done(int_pay)
                    logging.info(f"User {user_id} is automatically warned about his success topup №{int_pay}")
                    m_success_topup = (f"\U00002705 *Пополнение №{int_pay} успешно выполнено!*"
                                       f"\n\n*Ваш баланс:*\n{int(await db.get_user_balance(user_id))}₽")
                    await bot.send_message(user_id, m_success_topup, "Markdown",
                                           reply_markup=types.InlineKeyboardMarkup(1).add(await b().button_lk()))
                M += 1
            await asyncio.sleep(30)

    async def topup_checker_user(self, user_id, way_topup, id_pay, msg_id):
        if await db.get_topup_accured(id_pay) == 0:
            text = "*Поиск транзакции*\n\n"
            N = 5
            while N != 0:
                text += "\U000026AA"
                await bot.edit_message_text(text, user_id, msg_id, parse_mode="Markdown")
                await asyncio.sleep(1)
                N -= 1
            logging.info(f"User {user_id} unsuccessfully tried to find his topup №{id_pay}")
            await bot.edit_message_text("*Транзакция не найдена.\n\nПроверьте перевод еще раз, либо обратитесь к поддержке*",
                                        user_id, msg_id, reply_markup=types.InlineKeyboardMarkup(1).add(
                    await b().BT_Support(), types.InlineKeyboardButton('\U0000267B Проверить еще раз',
                                                  callback_data=f"check_topup_{way_topup}_{format(id_pay, '7')}")), parse_mode="Markdown")
        elif (await db.get_topup_accured(id_pay) == 1) & (
                await db.get_topup_done(id_pay) == 0):
            await db.set_topup_balance(user_id, await db.get_topup_sum(id_pay))
            await db.set_topup_done(id_pay)
            logging.info(f"User {user_id} successfully get his topup №{id_pay}")
            m_success_topup = (f"\U00002705 *Транзакция успешно выполнена!*"
                               f"\n\n*Ваш баланс:*\n{int(await db.get_user_balance(user_id))}₽")
            await bot.edit_message_text(m_success_topup, user_id, msg_id,
                                        reply_markup=types.InlineKeyboardMarkup().add(
                                            types.InlineKeyboardButton(await self.BT_lk(msg_id))),
                                        parse_mode="Markdown")
        elif await db.get_topup_done(id_pay) == 1:
            await bot.delete_message(user_id, msg_id)
            logging.info(f"User {user_id} tried to get his topup №{id_pay} again")
            await bot.send_message(user_id, "*Данная транзакция уже выполнена*",
                                   reply_markup=types.InlineKeyboardMarkup().add(
                                       await self.BT_close()), parse_mode="Markdown")

    async def data_checker(self, mfu):
        if (await db.get_user_name(mfu.id) != mfu.first_name) or (
                await db.get_user_lastname(mfu.id) != mfu.last_name) or (
                await db.get_user_username(mfu.id) != mfu.username):
            await db.update_data(mfu.first_name, mfu.last_name, mfu.username,
                                 mfu.id)

    async def bet_sum_checker(self, call, user_id=0, game="", sum=0):
        keyboard = types.InlineKeyboardMarkup()
        if call != 0:
            user_id = call.from_user.id
            game = call.data[-11:-7]
            sum = int(call.data[-6:].lstrip("0"))
        if sum <= int(await db.get_user_balance(user_id)):
            if call != 0 and call.data[:11] == "create_bet_":
                if call.data[11:15] in ("king", "russ", "duel"):
                    await games.Games().games_online(call.from_user.id, game, sum,
                                           call.message.message_id)
                elif call.data[11:15] in ("bowl", "cube", "slot"):
                    await games.Games().games_offline(call.from_user.id, game, sum,
                                            call.message.message_id)
                return
            else:
                gline = {
                    "duel": "Дуэль\U0001F93A",
                    "king": "Королевская битва\U0001F451",
                    "russ": "Русская рулетка\U0001F3B2",
                    "bowl": "Боулинг\U0001F3B3",
                    "cube": "Кубик\U0001F3B2",
                    "slot": "Рулетка\U0001F3B0"
                }[game]
                check_txt = (f"*Выбранные параметры:*\n\nИгра - *{gline}*\nСтавка - *{sum}₽\U0001F4B0*")
                keyboard.add(types.InlineKeyboardButton('\U00002705 Подтвердить',
                                                    callback_data=f"create_bet_{game}_{format(sum, '06')}"))
        elif sum > await db.get_user_balance(user_id):
            check_txt = (f"*Недостаточно средств:*\n\nБаланс - *{int(await db.get_user_balance(user_id))}₽*"
                         f"\nСтавка - *{sum}₽*")
            keyboard.add(types.InlineKeyboardButton('\U0001F4B5 Пополнить', callback_data=f"topup_balance_{game}"))
        keyboard.add(types.InlineKeyboardButton('\U0000267B Изменить', callback_data='change_bet'))
        if call != 0:
            await bot.edit_message_text(check_txt, user_id, call.message.message_id, reply_markup=keyboard,
                                        parse_mode="Markdown")
        else:
            await bot.send_message(user_id, check_txt, reply_markup=keyboard, parse_mode="Markdown")

    async def rules_checker(self, user_id):
        if not await db.get_rules_accept(user_id):
            logging.warning(f"User {user_id} tried to use Bot without rules accepting")
            await bot.send_message(user_id,
                                   "*Вы не можете пользоваться ботом, пока не приняли правила*",
                                   parse_mode="Markdown",
                                   reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
                                       types.KeyboardButton("\U0001F4D5 Правила"), types.KeyboardButton("\U00002705 Принять правила")
                                   ))
        elif await db.get_ban(user_id):
            logging.warning(f"User {user_id} tried to use Bot with ban")
            await bot.send_message(user_id, "*Вы заблокированы \n\nДля возможного снятия блокировки вы можете связаться с поддержкой*", parse_mode="Markdown",
                                   reply_markup=types.InlineKeyboardMarkup().add(
                                       await b().BT_Support()))
        return await db.get_rules_accept(user_id), await db.get_ban(user_id)

    async def winner_warned_checker(self):
        logging.info(f"Checking the notifications of the winners")
        while True:
            count_lines = await db.get_lines_no_warned()
            M = 0
            logging.info(f"Lines not warned winners - {count_lines}")
            while M < count_lines:
                id_game, num_win, warned, game = [x for x in await db.all_no_warned_checker(M)]
                g_line = {
                    "duel": "Дуэль",
                    "russ": "Русская рулетка",
                    "king": "Королевская битва",
                    "bowl": "Боулинг",
                    "cube": "Кубик",
                    "slot": "Рулетка"
                }[game]
                if num_win != 0 and warned is False:
                    if game in ("duel", "russ", "king"):
                        user_id, bet = [x for x in await db.get_winner(id_game, game, num_win)]
                        line = f"\U0001F389 *Вы победили в игре *\n{g_line} №{id_game}"\
                               f"\nВаш выигрыш - *{bet}₽*\nПроверьте свою удачу еще раз!\n"
                        await db.warned_winner(g_line, id_game)
                        await db.set_topup_balance(user_id, bet)
                    elif game in ("bowl", "cube", "slot"):
                        user_id, bet = [x for x in await db.get_winner(id_game, "offl", "_id")]
                        line = f"\U00002755 *Расчет за игру {g_line} №{id_game} был произведен*"
                        await db.warned_winner("offl", id_game)
                    key_again = types.InlineKeyboardButton(text='\U0000267B Попробовать еще раз',
                                                           callback_data='change_bet')
                    await bot.send_message(user_id, line, "Markdown",
                                           reply_markup=types.InlineKeyboardMarkup(1).add(key_again, await b().BT_Lk()))
                M += 1
            await asyncio.sleep(30)






