import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import conf
from db import BotDB as db
from buttonsTg import ButtonsTg as b
from texts import TextsTg as txt
bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot)
db = db('lotEasy.db')

class Checkers:

    async def topupChekerAll(self):
        N = True
        print("Checking users topups is enabled")
        while N != False:
            count_lines = int(await db.get_lines_no_topup())
            print("Lines not done topups - " + str(count_lines))
            M = 0
            while M < count_lines:
                lines = await db.all_no_topup_checker(M)
                int_pay = lines[0]
                user_id = lines[1]
                sum = lines[2]
                accrued = lines[3]
                done = lines[4]
                if (accrued == True) and (done == False):
                    await db.topup_balance(user_id, sum)
                    await db.set_topup_done(int_pay)
                    keyboard = types.InlineKeyboardMarkup();
                    m_success_topup = ("\U00002705 *Пополнение №" + str(int_pay) + " успешно выполнена!*"
                                       "\n\n*Ваш баланс:*\n" + str(int(await db.get_user_balance(user_id))) + "₽")
                    msg = await bot.send_message(text=m_success_topup, chat_id=user_id,
                                                      reply_markup=keyboard,
                                                      parse_mode="Markdown")
                    msg
                    button_back_acc = types.InlineKeyboardButton(text='\U0001F464 Личный кабинет',
                                                                 callback_data='back_to_acc_' + str(
                                                                     format(msg.message_id, '010')));
                    keyboard.add(button_back_acc)
                    await bot.edit_message_reply_markup(user_id, msg.message_id, reply_markup=keyboard)
                M += 1
            await asyncio.sleep(30)

    async def rules_checker(self, user_id, call):
        rules_acc = await db.get_rules_accept(user_id)
        if rules_acc == False:
            await b().ButtonRulesAccept(call)
        return rules_acc

    async def winnerWarnedChecker(self):
        N = True
        print("Checking the notifications of the winners")
        while N != False:
            count_lines = await db.get_lines_no_warned()
            M = 0
            print("Lines not warned winners - " + str(count_lines))
            while M < count_lines:
                lines = await db.all_no_warned_checker(M)
                id_game = lines[0]
                num_win = lines[1]
                warned = lines[2]
                game = lines[3]
                if game == "Дуэль":
                    g_line = "duel"
                elif game == "Русская рулетка":
                    g_line = "russ"
                elif game == "Королевская битва":
                    g_line = "king"
                if (num_win != 0) and (warned == False):
                    id_bet = await db.get_winner(id_game, g_line, num_win)
                    user_id = id_bet[0]
                    bet = id_bet[1]
                    line = "\U0001F389 *Вы победили в игре *\n" + game + " №" + str(id_game) +\
                           "\nВаш выигрыш - *" + str(bet) + "₽*\n" \
                                                              "Проверьте свою удачу еще раз!\n"
                    await db.topup_balance(user_id, bet)
                    await db.warned_winner(g_line, id_game)
                    msg = await bot.send_message(chat_id=user_id, text=line, parse_mode="Markdown")
                    msg
                    keyboard = types.InlineKeyboardMarkup(row_width=1)
                    key_again = types.InlineKeyboardButton(text='\U0000267B Попробовать еще раз',
                                                           callback_data='change_bet_' + str(
                                                               format(msg.message_id, '010')));
                    key_back_acc = types.InlineKeyboardButton(text='\U0001F464 Личный кабинет',
                                                              callback_data='back_to_acc_' + str(
                                                                  format(msg.message_id, '010')));
                    keyboard.add(key_again, key_back_acc)
                    await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)
                M += 1
            await asyncio.sleep(30)






