import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import conf
from db import BotDB as db
from texts import TextsTg as t
from buttonsTg import ButtonsTg as b
from fsm import FSM
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from checkers import Checkers as ch

storage = MemoryStorage()
db = db('lotEasy.db')
bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot, storage=storage)
print("\nBot successfully started!")

async def checkersStart():
    asyncio.gather(ch().topupChekerAll(), ch().winnerWarnedChecker())


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    m = message.from_user
    if(not await db.user_exists(m.id)):
        await db.add_user(m.id, m.first_name,
                          m.last_name, m.username)
        await b().ButtonRulesAcceptNew(message)
        if (await db.get_user_name(m.id) != m.first_name) or (await db.get_user_lastname(m.id) != m.last_name) or (await db.get_user_username(m.id) != m.username):
            await db.update_data(m.first_name, m.last_name, m.username, m.id)
    elif await db.get_rules_accept(m.id) == 0:
        await b().ButtonRulesAccept(message)
    else:
        await b().ButtonNotNew(message)
    await checkersStart()


@dp.message_handler(commands=['ppmanag'])
async def adm_manage(message: types.Message):
    m = message.from_user
    user_id = message.from_user.id
    if (await db.adm_check(user_id)):
        if (await db.adm_valid_check(user_id)):
            await b().ppmanag_main(message)
        else:
            await b().ppmanag_no_valid(message)
    else:
        await b().ppmanag_no(message)


#Выбор способа пополнения баланса. Запрос типа "top_up_balance_откуда перенаправило(04)_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:15] == "top_up_balance_")
async def way_topup(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        chat_id = call.message.chat.id
        way = call.data[15:19]
        await call.answer(text="Загрузка способов пополнения")
        msg_id = call.data[20:].lstrip("0")
        keyboard = types.InlineKeyboardMarkup(row_width=2);
        msg = await bot.edit_message_text(text=t.m_topup_way, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        msg
        key_topup_qiwi = types.InlineKeyboardButton(text='\U0001F95D QIWI',
                                                    callback_data='way_topup_qiwi_' + way + "_" + str(
                                                        format(msg.message_id, '010')));
        key_topup_bank = types.InlineKeyboardButton(text='\U0001F4B3 Карта',
                                                    callback_data='way_topup_bank_' + way + "_" + str(
                                                        format(msg.message_id, '010')));
        if way == "main":
            key_back = types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                      callback_data='back_to_acc_' + str(
                                                          format(msg.message_id, '010')));
        elif way == "king" or way == "duel" or way == "russ":
            key_back = types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                             callback_data='back_to_game_' + way + "_" + str(
                                                                 format(msg.message_id, '010')));
        keyboard.add(key_topup_bank, key_topup_qiwi);
        keyboard.row(key_back)
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


#Возвращения в аккаунт. Запрос типа "back_to_acc_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:12] == "back_to_acc_")
async def back_acc(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        await call.answer(text="Возвращение в аккаунт")
        keyboard = types.InlineKeyboardMarkup(row_width=2);
        msg_id = call.data[13:]
        acc_info = '*Мой аккаунт* \n\n\U0001F518 *Имя: *' + await db.get_user_name(user_id) + \
                   '\n\n\U0001F518*Баланс: *' + str(int(await db.get_user_balance(user_id))) + '₽' \
                                                                                            '\n\n\U0001F518*Дата регистрации: *' + str(
            str(await db.get_user_date(user_id))[:10]);
        msg = await bot.edit_message_text(text=acc_info, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
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
        await bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=keyboard)


#Выбор способа вывода. Запрос типа "withdraw_balance_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:17] == "withdraw_balance_")
async def way_with(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        chat_id = call.message.chat.id
        msg_id = call.data[18:].lstrip("0")
        keyboard = types.InlineKeyboardMarkup(row_width=2);
        await call.answer(text="Загрузка способов вывода")
        msg = await bot.edit_message_text(text=t.m_with_way, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        msg
        key_with_qiwi = types.InlineKeyboardButton(text='\U0001F95D QIWI',
                                                    callback_data='way_with_qiwi_' + str(
                                                        format(msg.message_id, '010')));
        key_with_bank = types.InlineKeyboardButton(text='\U0001F4B3 Карта',
                                                    callback_data='way_with_bank_' + str(
                                                        format(msg.message_id, '010')));
        key_back_acc = types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                  callback_data='back_to_acc_' + str(
                                                      format(msg.message_id, '010')));
        keyboard.add(key_with_bank, key_with_qiwi);
        keyboard.row(key_back_acc)
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


#Выбор суммы вывода. Запрос типа "way_with_способ(04)_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:9] == "way_with_")
async def choose_sum_with(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        chat_id = call.message.chat.id
        keyboard = types.InlineKeyboardMarkup(row_width=2);
        way_with = call.data[9:13]
        msg_id = call.data[14:].lstrip("0")
        await call.answer(text="Загрузка сумм вывода")
        if way_with == "qiwi":
            msg = await bot.edit_message_text(text=t.m_with_qiwi_sum, chat_id=chat_id, message_id=msg_id,
                                        parse_mode="Markdown")
        elif way_with == "bank":
            msg = await bot.edit_message_text(text=t.m_with_bank_sum, chat_id=chat_id, message_id=msg_id,
                                        parse_mode="Markdown")
        msg
        key_with_50 = types.InlineKeyboardButton(text='\U0001F4B4 50 ₽',
                                                  callback_data=way_with + '_withd_sum_000050_' + str(
                                                      format(msg.message_id, '010')));
        key_with_100 = types.InlineKeyboardButton(text='\U0001F4B5 100 ₽',
                                                   callback_data=way_with + '_withd_sum_000100_' + str(
                                                       format(msg.message_id, '010')));
        key_with_500 = types.InlineKeyboardButton(text='\U0001F4B6 500 ₽',
                                                   callback_data=way_with + '_withd_sum_000500_' + str(
                                                       format(msg.message_id, '010')));
        key_with_1000 = types.InlineKeyboardButton(text='\U0001F4B0 1000 ₽',
                                                    callback_data=way_with + '_withd_sum_001000_' + str(
                                                        format(msg.message_id, '010')));
        key_with_other = types.InlineKeyboardButton(text='\U0001F4DD Другая сумма',
                                                     callback_data=way_with + '_withd_other_sum_' + str(
                                                         format(msg.message_id, '010')));
        key_other_way = types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                   callback_data='withdraw_balance_' + str(
                                                       format(msg.message_id, '010')));
        keyboard.add(key_with_50, key_with_100, key_with_500, key_with_1000, key_with_other);
        keyboard.row(key_other_way)
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


#Ввод реквизитов вывода. Проверка возможности вывода введенной суммы. Запрос типа "способ(04)_withd_sum_сумма(06)_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[4:15] == "_withd_sum_")
async def enter_requi(call, state: FSMContext):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        msg_id = call.data[22:].lstrip("0")
        way_with = call.data[:4]
        sum_with = int(call.data[15:21].lstrip("0"));
        keyboard = types.InlineKeyboardMarkup(row_width=1);
        await call.answer(text="Загрузка ввода реквизитов")
        if sum_with <= int(await db.get_user_balance(user_id)):
            if way_with == "bank":
                msg = await bot.edit_message_text(text=t.m_enter_requisites_bank, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
            if way_with == "qiwi":
                msg = await bot.edit_message_text(text=t.m_enter_requisites_qiwi, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
            msg
            await state.update_data(msg = msg, way_with = way_with, sum_with= sum_with)
            await FSM.requisites.set()

        elif (sum_with) > int(await db.get_user_balance(user_id)):
            m_no_money = "\U0000274C *Недостаточно средств на балансе для вывода " + str(sum_with) + \
                         "₽\n\nВаш баланс: " + str(int(await db.get_user_balance(user_id))) + "₽*\n\nПопробуйте выбрать другую сумму"
            msg = await bot.edit_message_text(text=m_no_money, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
            msg
            button_back_money = types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                       callback_data='way_with_' + str(way_with) + '_' + str(
                                                           format(msg.message_id, '010')));
            button_back_acc = types.InlineKeyboardButton(text='\U0001F464 Личный кабинет', callback_data='back_to_acc_' + str(
                                                          format(msg.message_id, '010')));
            keyboard.add(button_back_acc, button_back_money);
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


#Вывод справок об играх. Из главного меню. Запрос типа "que_тип игры(04)_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:4] == "que_")
async def info_games(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        game = call.data[4:8]
        msg_id = call.data[9:]
        chat_id = call.message.chat.id
        await call.answer(text="Загрузка справки")
        keyboard = types.InlineKeyboardMarkup();
        if game == "russ":
            msg = await bot.edit_message_text(text=t.m_question_russ, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        elif game == "duel":
            msg = await bot.edit_message_text(text=t.m_question_duel, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        elif game == "king":
            msg = await bot.edit_message_text(text=t.m_question_king, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        msg
        button_check_top_up = types.InlineKeyboardButton(text='\U00002B05 Назад', callback_data='back_to_game_' + game + "_"+ str(format(msg.message_id, '010')));
        keyboard.add(button_check_top_up);
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


#Назад к играм. Запрос типа "back_to_game_игра(04)"
@dp.callback_query_handler(lambda call: call.data[:13] == "back_to_game_")
async def back_games(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        await call.answer(text="Возвращение к играм")
        game = call.data[13:17]
        msg_id = call.data[18:]
        call_send = 1
        await b().ButtonGameBet(game, call_send, call.from_user.id, call.message.chat.id, msg_id)


#Вывод списка операций. Переход из ЛК или выбора отображения всех операций. Запрос типа "story_topup_количество(0 - 10 шт, 1 - все)_айди сообщения"
@dp.callback_query_handler(lambda call: call.data[:12] == "story_topup_")
async def story_oper(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        await call.answer(text="Загрузка операций")
        if call.data[:14] == "story_topup_1_": #Для отображения всех
            msg_id = call.data[14:].lstrip("0")
        N = 10
        chat_id = call.message.chat.id
        lines_with = await db.get_withd_lines(call.from_user.id)
        lines_top = await db.get_topup_lines(call.from_user.id)
        count_lines = lines_top + lines_with
        keyboard = types.InlineKeyboardMarkup();
        if count_lines == 0:
            msg = await bot.send_message(chat_id,"У вас пока что нет пополнений", reply_markup=keyboard, parse_mode="Markdown")
            msg
            button_check_top_up = types.InlineKeyboardButton(text='\U0000274C Закрыть',
                                                             callback_data='delete_msg_' + str(
                                                                 format(msg.message_id, '010')));
            keyboard.add(button_check_top_up);
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)
        else:
            if ((call.data[:14] == "story_topup_1_") or (count_lines < N)):
                N = count_lines
            elif ((call.data[:14] == "story_topup_1_") and (count_lines > 20)):
                N = 20
            time_cr = str((await db.get_story(call.from_user.id, N))[5])
            dateline = "*• " + str(time_cr[:10]) + "*\n"
            dateold = time_cr[:10]
            story_topup = "*Последние " + str(N) +" операций:*\n\n" + dateline
            if count_lines < N:
                story_topup = "*Отображены последние " + str(N) + " операций:*\n\n" + dateline
            elif ((call.data[:14] == "story_topup_1_") and (count_lines > 20)):
                N = 20
                story_topup = "*Слишком много операций. Отображены последние " + str(N) + " операций:*\n\n" + dateline
            while N != 0:
                lines = await db.get_story(call.from_user.id, N)
                comm = lines[0]
                way = lines[1]
                sum = lines[2]
                done = lines[3]
                oper = lines[4]
                time_cr = str(lines[5])
                if oper == "Вывод":
                    requisites = (await db.get_requisites(comm)).strip(" ")
                    if len(str(requisites)) == 11:
                        req_line = "\nРеквизиты - _+" + str(requisites)[:3] + "••••" + str(requisites)[7:] + "_ \n"
                    elif len(str(requisites)) == 16:
                        req_line = "\nРеквизиты - _" + str(requisites)[:4] + "••••" + str(requisites)[12:] + "_ \n"
                else:
                    req_line = "\n"
                if (done == 0):
                    done = "\U0000274C"
                elif (done == 1):
                    done = "\U00002705"
                if way == "bank":
                    way = "Карта"
                elif way == "qiwi":
                    way = "QIWI"
                if dateold == time_cr[:10]:
                    line = "_-" + str((time_cr)[11:16]) + "_ - " + oper + " " + way + " - "+ str(sum) + "₽" + req_line + " (_№" + str(comm) + " " + done + ")_\n"
                if dateold != time_cr[:10]:
                    dateline = "\n*• " + str(time_cr[:10]) + "*\n"
                    line = dateline + "_-" + str((time_cr)[11:16]) + "_ - " + oper + " " + way + " - "+ str(sum) + "₽" + req_line + " (_№" + str(comm) + " "+ done + ")_\n"
                    dateold = time_cr[:10]
                story_topup = story_topup + line
                N-=1
            if call.data[:14] == "story_topup_1_":
                msg = await bot.edit_message_text(text=story_topup, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
            if call.data[:14] == "story_topup_0_":
                msg = await bot.send_message(call.from_user.id, text=story_topup, reply_markup=keyboard, parse_mode="Markdown")
                button_check_top_up = types.InlineKeyboardButton(text='Показать все', callback_data='story_topup_1_' + str(format(msg.message_id, '010')));
                keyboard.add(button_check_top_up);
            msg
            button_check_top_up = types.InlineKeyboardButton(text='\U0000274C Закрыть', callback_data='delete_msg_' + str(format(msg.message_id, '010')));
            keyboard.add(button_check_top_up);
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


# Выбор суммы пополнения. После выбора способа пополнения. Запрос типа "way_topup_способ(04)_откуда(04)_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:10] == "way_topup_")
async def choose_sum_topup(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        chat_id = call.message.chat.id
        await call.answer(text="Загрузка сумм вывода")
        keyboard = types.InlineKeyboardMarkup(row_width=2);
        way_topup = call.data[10:14]
        redir = call.data[15:19]
        msg_id = call.data[20:].lstrip("0")
        if way_topup == "qiwi":
            msg = await bot.edit_message_text(text=t.m_topup_qiwi_sum, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        elif way_topup == "bank":
            msg = await bot.edit_message_text(text=t.m_topup_bank_sum, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        msg
        key_topup_50 = types.InlineKeyboardButton(text='\U0001F4B4 50 ₽',
                                                  callback_data=way_topup + '_topup_sum_000050_' + str(
                                                      format(msg.message_id, '010')));
        key_topup_100 = types.InlineKeyboardButton(text='\U0001F4B5 100 ₽',
                                                   callback_data=way_topup + '_topup_sum_000100_' + str(
                                                       format(msg.message_id, '010')));
        key_topup_500 = types.InlineKeyboardButton(text='\U0001F4B6 500 ₽',
                                                   callback_data=way_topup + '_topup_sum_000500_' + str(
                                                       format(msg.message_id, '010')));
        key_topup_1000 = types.InlineKeyboardButton(text='\U0001F4B0 1000 ₽',
                                                    callback_data=way_topup + '_topup_sum_001000_' + str(
                                                        format(msg.message_id, '010')));
        key_topup_other = types.InlineKeyboardButton(text='\U0001F4DD Другая сумма',
                                                     callback_data=way_topup + '_topup_other_sum_' + str(
                                                         format(msg.message_id, '010')));
        key_other_way = types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                   callback_data='top_up_balance_' + redir + '_' + str(
                                                       format(msg.message_id, '010')));
        keyboard.add(key_topup_50, key_topup_100, key_topup_500, key_topup_1000, key_topup_other);
        keyboard.row(key_other_way)
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


# Вывод информации для пополнения. После успешного создания заявки на пополнение. Запрос типа "способ(04)_topup_sum_сумма(06)_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[4:15] == "_topup_sum_")
async def info_topup(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        await call.answer(text="Загрузка информации о пополнении")
        await bot.delete_message(chat_id, call.data[22:].lstrip("0"))
        way_topup = call.data[:4]
        sum_topup = call.data[15:21].lstrip("0");
        await db.topup_create(user_id, sum_topup, way_topup)
        keyboard = types.InlineKeyboardMarkup();
        get_comm = await db.get_comm(user_id, sum_topup, way_topup)
        if way_topup == "qiwi":
            m_topup_create = (t.m_topup_create_1 + str(sum_topup) + '₽* на QIWI кошелек *+79...* с комментарием "*№'
                            + str(get_comm) + '*"' + t.m_topup_create_2)
        elif way_topup == "bank":
            m_topup_create = (t.m_topup_create_1 + str(sum_topup) + '₽* на карту *1234...* с комментарием "*№'
                            + str(get_comm) + '*"' + t.m_topup_create_2)
        msg = await bot.send_message(user_id, text=m_topup_create, reply_markup=keyboard, parse_mode="Markdown")
        msg
        button_check_top = types.InlineKeyboardButton(text='\U00002705 Перевод выполнил', callback_data='check_topup_' + way_topup + "_" + str(format(get_comm, '7')) + "_" + str(format(msg.message_id, '010')));
        keyboard.add(button_check_top);
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


#Ручной ввод суммы пополнения или вывода. После выбора ручного ввода. Запрос типа "способ(04)_операция(05)_other_sum_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[10:21] == "_other_sum_")
async def enter_sum_topup(call, state: FSMContext):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        await call.answer(text="Загрузка поля ввода")
        chat_id = call.message.chat.id
        oper = call.data[5:10]
        msg_id = call.data[21:].lstrip("0")
        way = call.data[:4]
        keyboard = types.InlineKeyboardMarkup();
        if oper == "withd":
            msg = await bot.edit_message_text(text=t.m_enter_other_with, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
        elif oper == "topup":
            msg = await bot.edit_message_text(text=t.m_enter_other_top, chat_id=chat_id, message_id=msg_id,
                                        parse_mode="Markdown")
        msg
        await state.update_data(msg=msg, oper=oper, way=way)
        await FSM.other_sum.set()


#Удаления сообщения. Запрос типа "delete_msg_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:11] == "delete_msg_")
async def deleter(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        await call.answer(text="Закрытие сообщения")
        chat_id = call.message.chat.id
        await bot.delete_message(chat_id, call.data[11:].lstrip("0"))


#Проверка пополнения. Запрос типа "(re)check_topup_способ(04)_айди платежа(07)_ади сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:12] == "check_topup_" or call.data[:14] == "recheck_topup_")
async def check_topup(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        await call.answer(text="Проверка пополнения")
        if call.data[:12] == "check_topup_":
            N=0
        elif call.data[:14] == "recheck_topup_":
            N=2
        id_pay = call.data[17+N:24+N].lstrip("0")
        way_topup = call.data[12+N:16+N]
        user_id = call.from_user.id
        msg_id = call.data[25+N:35+N]
        await b().ButtonTopupCheck(user_id, way_topup, id_pay, msg_id, call)


#Создание заявки на вывод после подтверждения правильности данных. Запрос типа "confirm_with_способ(04)_сумма(06)_реквизиты(17)_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:13] == "confirm_with_")
async def create_withd(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        user_id = call.from_user.id
        chat_id = call.message.chat.id
        await call.answer(text="Загрузка подтверждения")
        keyboard = types.InlineKeyboardMarkup()
        way = call.data[13:17]
        sum = call.data[18:24].lstrip("0")
        requisites = call.data[25:42].lstrip("0")
        msg_id = call.data[43:]
        await db.with_create(user_id, sum, way, requisites)
        await db.withdraw_balance(user_id, sum)
        comm = await db.get_with(user_id, sum, way)
        m_with_create = "\U0000267B *Ваша заявка №" + str(
            comm) + " на сумму " + str(sum) + "₽ успешно зарегистрирована*" \
                                              "\n*Указанные реквизиты - " + str(requisites) + \
                                              "*\n\nВыполнение заявки может занимать до 24 часов"
        msg = await bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=m_with_create, parse_mode="Markdown")
        msg
        button_back_acc = types.InlineKeyboardButton(text='\U0001F464 Личный кабинет', callback_data='back_to_acc_' + str(
            format(msg.message_id, '010')));
        keyboard.add(button_back_acc);
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


#Проерка ставки и игры. Запрос типа "bet_игра(04)_сумма(06)_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:4] == "bet_")
async def check_bet(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        await call.answer(text="Проверка данных")
        keyboard = types.InlineKeyboardMarkup()
        game = call.data[4:8]
        sum = int(call.data[9:15].lstrip("0"))
        msg_id = call.data[16:]
        if game == "king":
            gline = "Королевская битва\U0001F451"
        elif game == "russ":
            gline = "Русская рулетка\U0001F3B2"
        elif game == "duel":
            gline = "Дуэль\U0001F93A"
        if sum <= int(await db.get_user_balance(call.from_user.id)):
            check_txt = ("*Выбранные параметры:*"
                         "\n\nИгра - *" + gline + "*"
                                                 "\nСтавка - *" + str(sum) + "₽\U0001F4B0*")
            msg = await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg_id, text=check_txt, parse_mode="Markdown")
            msg
            button_confirm_bet = types.InlineKeyboardButton(text='\U00002705 Подтвердить',
                                                            callback_data='create_bet_' + str(game) + "_" + str(
                                                                format(sum, '06')) + "_" + str(
                                                                format(msg.message_id, '010')));
            keyboard.add(button_confirm_bet)
        elif sum > await db.get_user_balance(call.from_user.id):
            check_txt = ("*Недостаточно средств:*"
                         "\n\nБаланс - *" + str(int(await db.get_user_balance(call.from_user.id))) + "₽*"
                                                 "\nСтавка - *" + str(sum) + "₽*")
            msg = await bot.edit_message_text(chat_id=call.message.chat.id, message_id=msg_id, text=check_txt, parse_mode="Markdown")
            msg
            key_topup = types.InlineKeyboardButton(text='\U0001F4B5 Пополнить', callback_data='top_up_balance_' + game + '_' + str(
                format(msg.message_id, '010')));
            keyboard.add(key_topup)
        button_change_bet = types.InlineKeyboardButton(text='\U0000267B Изменить',
                                                       callback_data='change_bet_' + str(
                                                                format(msg.message_id, '010')));
        keyboard.add(button_change_bet)
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=msg_id, reply_markup=keyboard)


#Изменение игры. Запрос типа "change_bet_айди сообщения(10)"
@dp.callback_query_handler(lambda call: call.data[:11] == "change_bet_")
async def changer_bet(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        if call.data[:11] == "change_bet_":
            await call.answer(text="Загрузка смены игры")
            msg_id = call.data[12:]
            call_send = 1
            await b().ButtonMainGames(call_send, call.from_user.id, call.message.chat.id, msg_id)


#Создание игровой комнаты и обработка игры. Запрос типа "create_bet_игра(04)_сумма(06)_айди сообщения(10). Перен"
@dp.callback_query_handler(lambda call: call.data[:11] == "create_bet_")
async def creating_room(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        await call.answer(text="Создание игры")
        user_id = call.from_user.id
        game = call.data[11:15]
        sum = call.data[16:22].lstrip("0")
        msg_id = call.data[23:]
        await b().GameProcess(user_id, game, sum, msg_id, call)

@dp.callback_query_handler(lambda call: call.data[:14] == "story_games_0_")
async def story_games(call):
    if await ch().rules_checker(call.from_user.id, call) == (True, False):
        await call.answer(text="Загрузка истории игр")
        if call.data[:14] == "story_topup_1_": #Для отображения всех
            msg_id = call.data[14:].lstrip("0")
        N = 10
        chat_id = call.message.chat.id
        lines_games = await db.get_games_lines()
        keyboard = types.InlineKeyboardMarkup();
        if lines_games == 0:
            msg = await bot.send_message(chat_id,"Вы пока что не сыграли ни в одну игру", reply_markup=keyboard, parse_mode="Markdown")
            msg
            button_check_top_up = types.InlineKeyboardButton(text='\U0000274C Закрыть',
                                                             callback_data='delete_msg_' + str(
                                                                 format(msg.message_id, '010')));
            keyboard.add(button_check_top_up);
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)
        else:
            if ((call.data[:14] == "story_topup_1_") or (count_lines < N)):
                N = count_lines
            elif ((call.data[:14] == "story_topup_1_") and (count_lines > 20)):
                N = 20
            time_cr = str((await db.get_story(call.from_user.id, N))[5])
            dateline = "*• " + str(time_cr[:10]) + "*\n"
            dateold = time_cr[:10]
            story_topup = "*Последние " + str(N) +" операций:*\n\n" + dateline
            if count_lines < N:
                story_topup = "*Отображены последние " + str(N) + " операций:*\n\n" + dateline
            elif ((call.data[:14] == "story_topup_1_") and (count_lines > 20)):
                N = 20
                story_topup = "*Слишком много операций. Отображены последние " + str(N) + " операций:*\n\n" + dateline
            while N != 0:
                lines = await db.get_story(call.from_user.id, N)
                comm = lines[0]
                way = lines[1]
                sum = lines[2]
                done = lines[3]
                oper = lines[4]
                time_cr = str(lines[5])
                if oper == "Вывод":
                    requisites = (await db.get_requisites(comm)).strip(" ")
                    if len(str(requisites)) == 11:
                        req_line = "\nРеквизиты - _+" + str(requisites)[:3] + "••••" + str(requisites)[7:] + "_ \n"
                    elif len(str(requisites)) == 16:
                        req_line = "\nРеквизиты - _" + str(requisites)[:4] + "••••" + str(requisites)[12:] + "_ \n"
                else:
                    req_line = "\n"
                if (done == 0):
                    done = "\U0000274C"
                elif (done == 1):
                    done = "\U00002705"
                if way == "bank":
                    way = "Карта"
                elif way == "qiwi":
                    way = "QIWI"
                if dateold == time_cr[:10]:
                    line = "_-" + str((time_cr)[11:16]) + "_ - " + oper + " " + way + " - "+ str(sum) + "₽" + req_line + " (_№" + str(comm) + " " + done + ")_\n"
                if dateold != time_cr[:10]:
                    dateline = "\n*• " + str(time_cr[:10]) + "*\n"
                    line = dateline + "_-" + str((time_cr)[11:16]) + "_ - " + oper + " " + way + " - "+ str(sum) + "₽" + req_line + " (_№" + str(comm) + " "+ done + ")_\n"
                    dateold = time_cr[:10]
                story_topup = story_topup + line
                N-=1
            if call.data[:14] == "story_topup_1_":
                msg = await bot.edit_message_text(text=story_topup, chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
            if call.data[:14] == "story_topup_0_":
                msg = await bot.send_message(call.from_user.id, text=story_topup, reply_markup=keyboard, parse_mode="Markdown")
                button_check_top_up = types.InlineKeyboardButton(text='Показать все', callback_data='story_topup_1_' + str(format(msg.message_id, '010')));
                keyboard.add(button_check_top_up);
            msg
            button_check_top_up = types.InlineKeyboardButton(text='\U0000274C Закрыть', callback_data='delete_msg_' + str(format(msg.message_id, '010')));
            keyboard.add(button_check_top_up);
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)



#Обработчик ручного ввода реквизитов вывода.
@dp.message_handler(content_types=types.ContentType.all(), state=FSM.requisites)
async def user_get_requisites(message: types.Message, state: FSMContext):
    data = await state.get_data()
    way = data['way_with']
    sum = data['sum_with']
    msg = data['msg']
    user_id = message.from_user.id
    chat_id = message.chat.id
    keyboard = types.InlineKeyboardMarkup()
    try:
        int(message.text)
        if ((way == "qiwi") and ((len(str(message.text)) != 11) or (message.text[:1] != "7"))) or (way == "bank") and (len(message.text) != 16):
            if (way == "qiwi") and (len(str(message.text)) != 11):
                txt_wrong = "*Неверная длина номера телефона.*\n\nНажмите на кнопку ниже и введите номер телефона еще раз"
                msg = await bot.send_message(chat_id, txt_wrong , reply_markup=keyboard, parse_mode="Markdown")
            elif (way == "qiwi") and (message.text[:1] != "7"):
                txt_wrong = "*Неверный номер телефона. Номер должен начинаться с 7.*\n\nНажмите на кнопку ниже и введите номер телефона еще раз"
                msg = await bot.send_message(chat_id, txt_wrong, reply_markup=keyboard, parse_mode="Markdown")
            elif (way == "bank") and (len(message.text) != 16):
                txt_wrong = "*Неверная длина номера карты.*\n\nНажмите на кнопку ниже и введите номер карты еще раз"
                msg = await bot.send_message(chat_id, txt_wrong, reply_markup=keyboard, parse_mode="Markdown")
            msg
            button_enter_again = types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                            callback_data=str(way) + '_withd_sum_' + str(format(sum, '06')) + str(
                                                                format(msg.message_id, '010')));
            button_back_acc = types.InlineKeyboardButton(text='\U0000274C Отмена',
                                                         callback_data='back_to_acc_' + str(
                                                             format(msg.message_id, '010')));
            keyboard.add(button_enter_again, button_back_acc);
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)
        else:
            requisites = str(message.text)
            if way == "qiwi":
                lineway = "QIWI"
                req = "Номер телефона - *+"
            elif way == "bank":
                lineway = "Карта"
                req = "Номер карты - *"
            msg = await bot.send_message(message.from_user.id, text="*Подтвердите правильность данных*"
                                                              "\n\nСумма - *" + str(sum) + '₽*'
                                                                '\nСпособ - *' + lineway +
                                                            '*\n' + req + str(requisites) + "*",
                                   reply_markup=keyboard, parse_mode="Markdown")
            msg
            button_confirm_withd = types.InlineKeyboardButton(text='\U00002705 Подтвердить',
                                                              callback_data='confirm_with_' + str(way) +
                                                                            "_" + str(format(sum, '06')) + "_" + str(format(requisites, '17')) + '_' + str(
                                                           format(msg.message_id, '010')));
            button_change_withd = types.InlineKeyboardButton(text='\U0000267B Изменить',
                                                           callback_data='withdraw_balance_' + str(
                                                                    format(msg.message_id, '010')));
            keyboard.add(button_confirm_withd, button_change_withd)
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)

    except:
        msg = await bot.send_message(message.from_user.id, text="*Неверный формат реквизитов. *"
                                                          "\n\nВыберите одно из действий",
                                   reply_markup=keyboard, parse_mode="Markdown")
        msg
        button_enter_again = types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                        callback_data=str(way) + '_withd_sum_' + str(
                                                            format(sum, '06')) + str(
                                                            format(msg.message_id, '010')));
        button_back_acc = types.InlineKeyboardButton(text='\U0000274C Отмена',
                                                     callback_data='back_to_acc_' + str(
                                                         format(msg.message_id, '010')));
        keyboard.add(button_enter_again, button_back_acc);
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)
    await state.finish()


#Обработчик ручного ввода суммы пополнения или вывода
@dp.message_handler(content_types=types.ContentType.all(), state=FSM.other_sum)
async def user_other_sum_enter(message, state: FSMContext):
    data = await state.get_data()
    way = data['way']
    oper = data['oper']
    msg = data['msg']
    keyboard = types.InlineKeyboardMarkup();
    if oper == "withd":
        lineoper = "вывода"
    if oper == "topup":
        lineoper = "пополнения"
    if way == "qiwi":
        lineway = "QIWI \U0001F95D"
    elif way == "bank":
        lineway = "Карта \U0001F4B3"
    try:
        int(message.text)
        if (int(message.text) > 10000) or (int(message.text) < 50):
            if (int(message.text) > 10000):
                msg = await bot.send_message(message.from_user.id, text = "*Максимальная сумма " + lineoper + " - 10000₽*"
                                                                "\n\nВыберите одно из действий",
                                   reply_markup=keyboard, parse_mode="Markdown")
            elif (int(message.text) < 50):
                msg = await bot.send_message(message.from_user.id, text="*Минимальная сумма " + lineoper + " - 50₽*"
                                                                  "\n\nВыберите одно из действий",
                                       reply_markup = keyboard, parse_mode = "Markdown")
            msg
            button_enter_again = types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                            callback_data=way + '_' + str(oper) + '_other_sum_' + str(
                                                                format(msg.message_id, '010')));
            button_back_acc = types.InlineKeyboardButton(text='\U0000274C Отмена',
                                                         callback_data='back_to_acc_' + str(
                                                             format(msg.message_id, '010')));
            keyboard.add(button_enter_again, button_back_acc);
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)
        else:
            sum_topup = int(message.text)
            msg = await bot.send_message(message.from_user.id, text="*Подтвердите правильность способа и суммы*"
                                                              "\n\nСумма " + lineoper + " - *" + str(sum_topup) + '₽*'
                                                                '\nСпособ ' + lineoper + ' - *' + str(lineway) + "*",
                                   reply_markup=keyboard, parse_mode="Markdown")
            msg
            button_check_top = types.InlineKeyboardButton(text='\U00002705 Подтвердить', callback_data=str(way) + '_' + str(oper) + '_sum_' + str(format(sum_topup, '06')) + "_" + str(
                                                           format(msg.message_id, '010')));
            keyboard.add(button_check_top);
            if oper == "withd":
                button_change = types.InlineKeyboardButton(text='\U0000267B Изменить',
                                                           callback_data='withdraw_balance_' + str(
                                                                    format(msg.message_id, '010')));
            if oper == "topup":
                button_change = types.InlineKeyboardButton(text='\U0000267B Изменить',
                                                              callback_data='top_up_balance_main_' + str(
                                                                   format(msg.message_id, '010')));
            keyboard.add(button_change);
            await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)
    except:
        msg = await bot.send_message(message.from_user.id, text="*Неверный формат числа. *"
                                                          "\n\nВыберите одно из действий",
                                   reply_markup=keyboard, parse_mode="Markdown")
        msg
        button_enter_again = types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                        callback_data=way + '_' + str(oper) + '_other_sum_' + str(
                                                            format(msg.message_id, '010')));
        button_back_acc = types.InlineKeyboardButton(text='\U0000274C Отмена',
                                                     callback_data='back_to_acc_' + str(
                                                         format(msg.message_id, '010')));
        keyboard.add(button_enter_again, button_back_acc);
        await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)
    await state.finish()


@dp.message_handler(lambda message: message.text == "\U0001F464 Личный кабинет")
async def account(message):
    await b().ButtonAccount(message)


@dp.message_handler(lambda message: message.text == "\U0001F4AC Правила")
async def main_rules(message):
    keyboard = types.InlineKeyboardMarkup();
    msg = await bot.send_message(message.from_user.id, text=t.m_rules, reply_markup=keyboard, parse_mode="Markdown")
    msg
    button_delete = types.InlineKeyboardButton(text='\U0000274C Закрыть',
                                               callback_data='delete_msg_' + str(format(msg.message_id, '010')));
    keyboard.add(button_delete);
    await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "\U0001F4AC Поддержка")
async def main_rules(message):
    await message.delete()
    keyboard = types.InlineKeyboardMarkup();
    msg = await bot.send_message(message.from_user.id, text=t.m_support, reply_markup=keyboard, parse_mode="Markdown")
    msg
    button_delete = types.InlineKeyboardButton(text='\U0000274C Закрыть',
                                               callback_data='delete_msg_' + str(format(msg.message_id, '010')));
    keyboard.add(button_delete);
    await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "\U0001F4D5 Правила")
async def main_new_rules(message):
    await message.delete()
    msg = await bot.send_message(message.from_user.id, text=t.m_rules, parse_mode="Markdown")
    msg


@dp.message_handler(lambda message: message.text == "\U00002705 Принять правила")
async def main_start(message):
    await b().ButtonCmdStart(message)
    await db.rules_accept(message.from_user.id)


@dp.message_handler(lambda message: message.text == "\U00002139 Меню" or
                     message.text == "\U00002B05 Вернуться в меню" or message.text == "\U0001F680 Начать пользование")
async def main(message: types.Message):
    user_id = message.from_user.id
    await b().ButtonMenu(user_id)


@dp.message_handler(lambda message: message.text == "\U0001F3AE Игры" or message.text == "\U00002B05 Вернуться к играм")
async def main_games(message):
    call_send = 0
    await b().ButtonMainGames(call_send, message.from_user.id, message.chat.id, message.message_id)


@dp.message_handler(lambda message: message.text == "\U00002139 Справка")
async def info_bot(message):
    await b().ButtonInfo(message.from_user.id)


@dp.message_handler(lambda message: message.text == "\U0001F4AC Комиссия")
async def where_10(message):
    await message.delete()
    keyboard = types.InlineKeyboardMarkup();
    msg = await bot.send_message(message.from_user.id, text=t.m_where10, reply_markup=keyboard, parse_mode="Markdown")
    msg
    button_delete = types.InlineKeyboardButton(text='\U0000274C Закрыть',
                                               callback_data='delete_msg_' + str(format(msg.message_id, '010')));
    keyboard.add(button_delete);
    await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "\U0001F4AC Алгоритмы")
async def what_random(message):
    await message.delete()
    keyboard = types.InlineKeyboardMarkup();
    msg = await bot.send_message(message.from_user.id, text=t.m_why_rand, reply_markup=keyboard, parse_mode="Markdown")
    msg
    button_delete = types.InlineKeyboardButton(text='\U0000274C Закрыть',
                                               callback_data='delete_msg_' + str(format(msg.message_id, '010')));
    keyboard.add(button_delete);
    await bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "\U0001F93A Дуэль")
async def duel_game_bet(message):
    call_send = 0
    game = "duel"
    await b().ButtonGameBet(game, call_send, message.from_user.id, message.chat.id, message.message_id)


@dp.message_handler(lambda message: message.text == "\U0001F3B2 Русская рулетка")
async def rus_game_bet(message):
    call_send = 0
    game = "russ"
    await b().ButtonGameBet(game, call_send, message.from_user.id, message.chat.id, message.message_id)


@dp.message_handler(lambda message: message.text == "\U0001F451 Королевская битва")
async def king_game_bet(message):
    call_send = 0
    game = "king"
    await b().ButtonGameBet(game, call_send, message.from_user.id, message.chat.id, message.message_id)

executor.start_polling(dp)