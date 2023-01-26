import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import conf
import random
from texts import TextsTg as txt
from db import BotDB as db

bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot)


db = db('lotEasy.db')


class ButtonsTg:

    async def save_msg(self, msg):
        await db.message_saver(msg.message_id, msg.chat.id, str(msg.text))

    async def ButtonRulesAcceptNew(self, message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button_reg = types.KeyboardButton(text="\U00002705 Принять правила")
        button_rules = types.KeyboardButton(text="\U0001F4D5 Правила")
        keyboard.add(button_reg, button_rules)
        msg = await bot.send_message(message.from_user.id, text=txt.m_hello_new, reply_markup=keyboard, parse_mode="Markdown")
        msg

    async def ButtonRulesAccept(self, call):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button_reg = types.KeyboardButton(text="\U00002705 Принять правила")
        button_rules = types.KeyboardButton(text="\U0001F4D5 Правила")
        keyboard.add(button_reg, button_rules)
        msg = await bot.send_message(call.from_user.id, text=txt.m_no_rules, reply_markup=keyboard, parse_mode="Markdown")
        msg

    async def ButtonCmdStart(self, message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_reg = types.KeyboardButton(text="\U0001F680 Начать пользование")
        keyboard.add(button_reg)
        await bot.send_message(message.from_user.id, text=txt.m_start_new, reply_markup=keyboard)

    async def ButtonNotNew(self, message):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_reg = types.KeyboardButton(text="\U00002139 Меню")
        keyboard.add(button_reg)
        msg = await bot.send_message(message.from_user.id, text=txt.m_hello_old, reply_markup=keyboard)
        msg

    async def ButtonMenu(self, user_id):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button_account = types.KeyboardButton(text="\U0001F464 Личный кабинет")
        button_to_games = "\U0001F3AE Игры"
        button_games_info = "\U00002139 Справка"
        keyboard.add(button_account, button_to_games, button_games_info)
        msg = await bot.send_message(user_id, text=txt.m_you_in_menu, reply_markup=keyboard)
        msg

    async def ButtonGameBet(self, game, call_send, user_id, chat_id, msg_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2);
        if game == "king":
            sh_txt = txt.m_bet_king
        elif game == "russ":
            sh_txt = txt.m_bet_russ
        elif game == "duel":
            sh_txt = txt.m_bet_duel
        if call_send == 1:
            msg = await bot.edit_message_text(text=sh_txt, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        if call_send == 0:
            msg = await bot.send_message(user_id, text=sh_txt, reply_markup=keyboard,
                                   parse_mode="Markdown")
        msg
        key_50 = types.InlineKeyboardButton(text='\U0001F4B4 50 ₽', callback_data='bet_' + game + '_000050_' + str(
            format(msg.message_id, '010')));
        key_100 = types.InlineKeyboardButton(text='\U0001F4B5 100 ₽', callback_data='bet_' + game + '_000100_' + str(
            format(msg.message_id, '010')));
        key_500 = types.InlineKeyboardButton(text='\U0001F4B6 500 ₽', callback_data='bet_' + game + '_000500_' + str(
            format(msg.message_id, '010')));
        key_1000 = types.InlineKeyboardButton(text='\U0001F4B0 1000 ₽', callback_data='bet_' + game + '_001000_' + str(
            format(msg.message_id, '010')));
        key_que = types.InlineKeyboardButton(text='\U00002753 Справка', callback_data='que_' + game + '_' + str(
            format(msg.message_id, '010')));
        keyboard.add(key_50, key_100, key_500, key_1000, key_que);
        await bot.edit_message_reply_markup(chat_id=msg.chat.id, message_id=msg.message_id, reply_markup=keyboard)


    async def ButtonMainGames(self, call_send, user_id, chat_id, msg_id):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        button_to_duel = "\U0001F93A Дуэль"
        button_to_russian = "\U0001F3B2 Русская рулетка"
        button_to_king = "\U0001F451 Королевская битва"
        button_back_to_main = "\U00002B05 Вернуться в меню"
        keyboard.add(button_to_duel, button_to_russian, button_to_king, button_back_to_main)
        if call_send == 1:
            msg = await bot.edit_message_text(text=txt.m_games_choose, chat_id=chat_id, message_id=msg_id,
                                        parse_mode="Markdown")
        elif call_send == 0:
            msg = await bot.send_message(user_id, text=txt.m_games_choose, reply_markup=keyboard)
        msg

    async def ButtonInfo(self, user_id):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button_where_10 = "\U0001F4AC Комиссия"
        button_why_trust = "\U0001F4AC Алгоритмы"
        button_rules = types.KeyboardButton(text="\U0001F4AC Правила")
        button_support = types.KeyboardButton(text="\U0001F4AC Поддержка")
        button_back_to_menu = types.KeyboardButton(text="\U00002B05 Вернуться в меню")
        keyboard.add(button_where_10, button_why_trust, button_rules, button_support, button_back_to_menu)
        msg = await bot.send_message(user_id, text=txt.m_main_info, reply_markup=keyboard, parse_mode="Markdown")
        msg

    async def ButtonTopup(self, user_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2);
        msg = await bot.send_message(user_id, text=txt.m_topup_way, reply_markup=keyboard, parse_mode="Markdown")
        msg
        key_topup_qiwi = types.InlineKeyboardButton(text='\U0001F95D QIWI',
                                                    callback_data='way_topup_qiwi_' + str(
                                                        format(msg.message_id, '010')));
        key_topup_bank = types.InlineKeyboardButton(text='\U0001F4B3 Карта',
                                                    callback_data='way_topup_bank_' + str(
                                                        format(msg.message_id, '010')));
        key_back_acc = types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                  callback_data='back_to_acc_' + str(
                                                      format(msg.message_id, '010')));
        keyboard.add(key_topup_qiwi, key_topup_bank);
        keyboard.row(key_back_acc)
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)

    async def ButtonTopupSum(self, user_id, way_topup):
        keyboard = types.InlineKeyboardMarkup(row_width=2);
        if way_topup == "qiwi":
            msg = await bot.send_message(user_id, text=txt.m_topup_qiwi_sum, reply_markup=keyboard, parse_mode="Markdown")
        elif way_topup == "bank":
            msg = await bot.send_message(user_id, text=txt.m_topup_bank_sum, reply_markup=keyboard, parse_mode="Markdown")
        msg
        key_topup_50 = types.InlineKeyboardButton(text='\U0001F4B4 50 ₽',
                                                  callback_data=way_topup + '_topup_sum_000050' + str(
                                                      format(msg.message_id, '010')));
        key_topup_100 = types.InlineKeyboardButton(text='\U0001F4B5 100 ₽',
                                                   callback_data=way_topup + '_topup_sum_000100' + str(
                                                       format(msg.message_id, '010')));
        key_topup_500 = types.InlineKeyboardButton(text='\U0001F4B6 500 ₽',
                                                   callback_data=way_topup + '_topup_sum_000500' + str(
                                                       format(msg.message_id, '010')));
        key_topup_1000 = types.InlineKeyboardButton(text='\U0001F4B0 1000 ₽',
                                                    callback_data=way_topup + '_topup_sum_001000' + str(
                                                        format(msg.message_id, '010')));
        key_topup_other = types.InlineKeyboardButton(text='\U0001F4DD Другая сумма',
                                                     callback_data=way_topup + '_topup_other_sum_' + str(
                                                         format(msg.message_id, '010')));
        key_other_way = types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                   callback_data='top_up_balance_main_' + str(
                                                       format(msg.message_id, '010')));
        keyboard.add(key_topup_50, key_topup_100, key_topup_500, key_topup_1000, key_topup_other);
        keyboard.row(key_other_way)
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)

    async def ButtonSupport(self, user_id, id_pay, way_topup, msg_id, call):
        keyboard = types.InlineKeyboardMarkup();
        button_support = types.InlineKeyboardButton(text='Связаться с поддержкой', url="https://t.me/OrAndOn");
        keyboard.add(button_support);
        look = txt.m_look_topup
        msg = await bot.edit_message_text(text=look, chat_id=call.message.chat.id, message_id=msg_id, parse_mode="Markdown")
        msg
        id_pay = id_pay.lstrip(" ")
        N = 5
        while N != 1:
            await asyncio.sleep(1)
            look = look + "\U000026AA"
            if await db.get_topup_accured(id_pay) == 0:
                msg = await bot.edit_message_text(look, msg.chat.id, msg.message_id, parse_mode="Markdown")
                msg
                N -= 1
            elif await db.get_topup_accured(id_pay) == 1:
                break
        if await db.get_topup_accured(id_pay) == 0:
            if way_topup == "bank":
                line_req = "Карта - *1234...*"
            if way_topup == "qiwi":
                line_req = "QIWI кошелек - *+79...*"
            no_topup = ("\U0000274C *Перевод не найден*"
                        "\n\nПроверьте правильность реквизитов и комментария к переводу:\n"
                        "\n" + line_req + ""
                                          "\nКомментарий - *№" + str(id_pay) + "*")
            await bot.edit_message_text(no_topup, msg.chat.id, msg.message_id, parse_mode="Markdown")
            button_recheck = types.InlineKeyboardButton(text='\U0000267B Проверить заново',
                                                        callback_data='recheck_topup_' + way_topup + "_" + str(
                                                            format(id_pay, '7')) + "_" + str(
                                                            format(msg.message_id, '010')));
            keyboard.add(button_recheck);
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)
        elif await db.get_topup_accured(id_pay) == 1:
            await self.ButtonTopupCheck(user_id, way_topup, id_pay, msg.message_id, call)

    async def ButtonTopupAlreadyDone(self, user_id):
        keyboard = types.InlineKeyboardMarkup();
        msg = await bot.send_message(user_id, text=txt.m_topup_already_done, reply_markup=keyboard, parse_mode="Markdown")
        msg
        button_close = types.InlineKeyboardButton(text='\U0000274C Закрыть',
                                                  callback_data='delete_msg_' + str(
                                                      format(msg.message_id, '010')));
        keyboard.add(button_close);
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)

    async def ButtonTopupCheck(self, user_id, way_topup, id_pay, msg_id, call):
        if await db.get_topup_accured(id_pay) == 0:
            await ButtonsTg().ButtonSupport(user_id, id_pay, way_topup, msg_id, call)
        elif (await db.get_topup_accured(id_pay) == 1) & (
                await db.get_topup_done(id_pay) == 0):
            sum_topup = await db.get_topup_sum(id_pay)
            await db.topup_balance(user_id, sum_topup)
            await db.set_topup_done(id_pay)
            keyboard = types.InlineKeyboardMarkup();
            m_success_topup = ("\U00002705 *Dранзакция успешно выполнена!*"
                               "\n\n*Ваш баланс:*\n" + str(int(await db.get_user_balance(user_id))) + "₽")
            msg = await bot.edit_message_text(text=m_success_topup, chat_id=call.message.chat.id, message_id=msg_id,
                                        parse_mode="Markdown")
            msg
            button_back_acc = types.InlineKeyboardButton(text='\U0001F464 Личный кабинет',
                                                         callback_data='back_to_acc_' + str(
                                                             format(msg.message_id, '010')));
            keyboard.add(button_back_acc)
            await bot.edit_message_reply_markup(call.message.chat.id, msg.message_id, reply_markup=keyboard)
        elif await db.get_topup_done(id_pay) == 1:
            await bot.delete_message(call.message.chat.id, msg_id)
            await ButtonsTg().ButtonTopupAlreadyDone(user_id)

    async def ButtonAccount(self, message):
        user_id = message.from_user.id
        keyboard = types.InlineKeyboardMarkup(row_width=2);
        acc_info = '*Мой аккаунт* \n\n\U0001F518 *Имя: *' + await db.get_user_name(user_id) + \
                   '\n\n\U0001F518*Баланс: *' + str(int(await db.get_user_balance(user_id))) + '₽' \
                                                                                            '\n\n\U0001F518*Дата регистрации: *' + str(
            str(await db.get_user_date(user_id))[:10]);
        msg = await bot.send_message(message.from_user.id, text=acc_info, reply_markup=keyboard, parse_mode="Markdown")
        msg
        key_topup = types.InlineKeyboardButton(text='\U0001F4B5 Пополнить', callback_data='top_up_balance_main_' + str(
            format(msg.message_id, '010')));
        key_withdraw = types.InlineKeyboardButton(text="\U0001F4B8 Вывести", callback_data='withdraw_balance_' + str(
            format(msg.message_id, '010')));
        key_story_topup = types.InlineKeyboardButton(text="\U0001F4D6 Операции", callback_data='story_topup_0_')
        key_story_games = types.InlineKeyboardButton(text="\U0001F3B2 История игр", callback_data='story_games_0_')
        keyboard.add(key_topup, key_withdraw)
        keyboard.row(key_story_topup)
        keyboard.row(key_story_games)
        await bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=msg.message_id, reply_markup=keyboard)

    async def GameProcess(self, user_id, game, sum, msg_id, call):
        await db.withdraw_balance(user_id, sum)
        cur_user = 2
        if game == "king":
            gline = "\U0001F451 Королевская битва"
            max_num_user = 100
        elif game == "russ":
            gline = "\U0001F3B2 Русская рулетка"
            max_num_user = 6
        elif game == "duel":
            gline = "\U0001F93A Дуэль"
            max_num_user = 2
        while cur_user < max_num_user + 1:
            free_room = await db.game_check_free(game, cur_user, user_id, sum)
            if free_room != None:
                break
            cur_user += 1
        if free_room == None:
            await db.game_create(game, user_id, sum)
            num_user = 1
        elif free_room != None:
            if ((game == "duel") or (game =="russ")) and (cur_user == max_num_user):
                full = True
            elif ((game == "duel") or (game =="russ")) and (cur_user != max_num_user):
                full = False
            elif (game == "king") and (cur_user == 8):
                full = True
            await db.game_add_user(game, cur_user, free_room, user_id, full)
            num_user = cur_user
        id_room = await db.game_get_id(game, num_user, user_id, sum)
        if game == "duel":
            num_enemys = "\n\nОжидание противника\n"
        else:
            num_enemys = "\n\nОжидание противников\n"
        create_txt = ("*Вы успешно присоединились к игре*\n"
                      "Комната - *" + str(id_room) +
                      "*\nВаш номер - *№" + str(num_user) + "*"
                                                            "\n\n*" + str(gline) + "*"
                                                                                   "\n\U0001F4B0*" + str(
                    sum) + "₽*") + num_enemys
        edited_txt = create_txt
        msg = await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg_id, text=create_txt,
                                    parse_mode="Markdown")
        msg
        N = 6
        while N != 0:
            await asyncio.sleep(1)
            if await db.game_check_full(game, id_room) == True:
                break
            edited_txt = edited_txt + "\U000026AA"
            msg = await bot.edit_message_text(edited_txt, msg.chat.id, msg.message_id, parse_mode="Markdown")
            msg
            N -= 1
            if N == 1:
                N = 6
                edited_txt = create_txt
        if game == "duel":
            enemy_found = "*\U00002705 Противник найден!*\n\nНачинаем игру..."
        else:
            enemy_found = "*\U00002705 Противники найдены!*\n\nНачинаем игру..."
        msg = await bot.edit_message_text(enemy_found, msg.chat.id, msg.message_id, parse_mode="Markdown")
        msg
        await asyncio.sleep(3)
        game_start = (gline[:1] + " Игра началась\n"
                                  "Ваше число - *" + str(num_user) + "*"
                                                                     "\n\nПроисходит выбор числа"
                                                                     "\n\U000026AA")
        msg = await bot.edit_message_text(game_start, msg.chat.id, msg.message_id, parse_mode="Markdown")
        msg
        N = 5
        while N != 1:
            await asyncio.sleep(1)
            game_start = game_start + "\U000026AA"
            msg = await bot.edit_message_text(game_start, msg.chat.id, msg.message_id, parse_mode="Markdown")
            msg
            N -= 1
        if await db.win_num_check(game, id_room) == 0:
            win_num = random.randint(1, max_num_user)
            await db.win_num_in(game, win_num, id_room)
        win_num = await db.win_num_check(game, id_room)
        win_bet = int(sum) * 2
        line_all = "*Выпало число " + str(win_num) + "*\n\n"
        if num_user == win_num:
            line = "\U0001F389 *Вы победили!*\n" + line_all + \
                   "Ваш выигрыш - *" + str(win_bet) + "₽*\n" \
                                                      "Проверьте свою удачу еще раз!\n"
            await db.topup_balance(user_id, win_bet)
            await db.warned_winner(game, id_room)
        elif num_user != win_num:
            line = "\U0001F383 *Вы проиграли*\n" + line_all + \
                   "Проверьте свою удачу еще раз!\n"
        msg = await bot.edit_message_text(line, msg.chat.id, msg.message_id, parse_mode="Markdown")
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
