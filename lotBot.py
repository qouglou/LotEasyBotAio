import asyncio
import random

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from magic_filter import F
from aiogram.filters.command import Command
import conf
import logging

from db import BotDB
from fsm import FSM
from texts import TextsTg as t
from buttons import ButtonsTg as b
from aiogram.fsm.storage.memory import MemoryStorage
from checkers import Checkers as ch
from messages import Messages as msg

db = BotDB('lotEasy.db')
bot = Bot(token=conf.TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(
    level=logging.WARNING,
    filename="difs/logs.log",
    format="%(asctime)s %(levelname)s %(funcName)s %(message)s")
logging.info("Bot successfully started!")


# Запуск бота
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if not await db.get_user_exists(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name,
                          message.from_user.last_name, message.from_user.username)
        logging.info(f"User {message.from_user.id} start to use Bot with message {message}")
        await msg().rules_accept(message.from_user.id, True)
    await ch().data_checker(message.from_user)
    if await db.get_rules_accept(message.from_user.id) == 0:
        await msg().rules_accept(message.from_user.id, False)
    else:
        await msg().not_new(message.from_user.id)


# Вызов основной админской панели BPManager через команду
@dp.message(Command("bpm"))
async def adm_manage_cmd(message: types.Message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        if await db.adm_check(message.from_user.id):
            if await db.adm_valid_check(message.from_user.id):
                text, keyboard = await b().KBT_Bpmanag(message.from_user.id)
                await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")
            else:
                logging.warning(
                    f"Not valid admin {message.from_user.id} tried to get access to admin panel with message - {message}")
                await msg().adm_no_valid(message.from_user.id, False)
        else:
            logging.warning(f"User {message.from_user.id} tried to get access to admin panel with message - {message}")
            await msg().bpmanag_no(message.from_user.id)


# Вызов основной админской панели BPManager через callback. Запрос типа main_bpmanag
@dp.callback_query(lambda call: call.data[:13] == "main_bpmanag")
async def adm_manage_call(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_check(call.from_user.id):
            if await db.adm_valid_check(call.from_user.id):
                text, keyboard = await b().KBT_Bpmanag(call.from_user.id)
                await bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=keyboard,
                                            parse_mode="Markdown")
            else:
                logging.warning(
                    f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
                await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)
        else:
            logging.warning(f"User {call.from_user.id} tried to get access to admin panel with message - {call}")
            await msg().bpmanag_no(call.from_user.id)


# Выбор способа пополнения/вывода баланса. Запрос типа "тип транзакции(05)_balance_откуда перенаправило(04)"
@dp.callback_query(lambda call: call.data[5:14] == "_balance_")
async def way_tw(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        way = call.data[14:18]
        if way == "main":
            b_back = await b().BT_Lk("\U00002B05")
        else:
            b_back = types.InlineKeyboardButton(text='\U00002B05 Назад', callback_data=f"back_to_game_{way}")
        buttons = [
            [
                types.InlineKeyboardButton(text='\U0001F95D QIWI',
                                           callback_data=f"way_{call.data[:5]}_qiwi_{way}"),
                types.InlineKeyboardButton(text='\U0001F4B3 Карта',
                                           callback_data=f"way_{call.data[:5]}_bank_{way}")
            ],
            [b_back]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        await bot.edit_message_text(t.dct_type_way[call.data[:5]], call.from_user.id, call.message.message_id,
                                    reply_markup=keyboard, parse_mode="Markdown")


# Возвращения в аккаунт. Запрос типа "back_to_acc"
@dp.callback_query(lambda call: call.data[:12] == "back_to_acc")
async def back_acc(call):
    await ch().data_checker(call.from_user)
    if await ch().rules_checker(call.from_user.id) == (True, False):
        text, keyboard = await b().KBT_Account(call.from_user.id)
        await bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                    reply_markup=keyboard, parse_mode="Markdown")


# Ввод реквизитов вывода. Проверка возможности вывода введенной суммы. Запрос типа "способ(04)_withd_sum_сумма(06)"
@dp.callback_query(lambda call: call.data[4:15] == "_withd_sum_")
async def enter_req(call, state: FSMContext):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        way_withd = call.data[:4]
        sum_with = int(call.data[15:21].lstrip("0"))
        if sum_with <= await db.get_user_balance(call.from_user.id):
            await bot.edit_message_text(t.dct_enter_req[way_withd], call.from_user.id, call.message.message_id,
                                        parse_mode="Markdown")
            await state.update_data(way_withd=way_withd, sum_with=sum_with)
            await state.set_state(FSM.requisites)
        elif sum_with > await db.get_user_balance(call.from_user.id):
            m_no_money = f"\U0000274C *Недостаточно средств на балансе для вывода {sum_with}₽" \
                         f"\n\nВаш баланс: {await db.get_user_balance(call.from_user.id)}₽*\n\nПопробуйте выбрать другую сумму"
            await bot.edit_message_text(m_no_money, call.from_user.id, call.message.message_id,
                                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[await b().BT_Lk()]),
                                        parse_mode="Markdown")


# Вывод справок об играх. Из главного меню. Запрос типа "que_тип игры(04)"
@dp.callback_query(lambda call: call.data[:4] == "que_")
async def info_games(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await bot.edit_message_text(t.dct_games_que[call.data[4:8]], call.from_user.id, call.message.message_id,
                                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                        types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                                   callback_data=f"back_to_game_{call.data[4:8]}")
                                    ]), parse_mode="Markdown")


# Назад к играм. Запрос типа "back_to_game_игра(04)"
@dp.callback_query(lambda call: call.data[:13] == "back_to_game_")
async def back_games(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        text, keyboard = await b().KBT_GameBet(call.data[13:17])
        await bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=keyboard,
                                    parse_mode="Markdown")


# Вывод списка операций. Переход из ЛК или кнопок вперед/назад. Имеет пагинацию". Запрос типа story_пользователь или админ(05)_номер страницы(07)_айди пользователя
@dp.callback_query(lambda call: call.data[:12] in ("story_topup_", "story_toadm_"))
async def story_oper(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if call.data[6:11] == "toadm":
            if await db.adm_valid_check(call.from_user.id):
                user_id = call.data[20:]
                adm_line = f"<b>Операции пользователя - <code>{user_id}</code></b>\n\n"
            else:
                logging.warning(
                    f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
                return await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)
        else:
            adm_line = ""
            user_id = call.from_user.id
        N = conf.base_num
        count_lines = await db.get_topup_lines(user_id) + await db.get_withd_lines(user_id)
        buttons = []
        if count_lines == 0:
            buttons.append(await b().BT_Close())
            if call.data[6:11] == "toadm":
                await call.message.answer("<b>У пользователя нет операций</b>",
                                          reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[buttons]),
                                          parse_mode="HTML")
            else:
                await call.message.answer("<b>У вас пока что нет операций</b>",
                                          reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[buttons]),
                                          parse_mode="HTML")
        else:
            current_page = int(call.data[12:19])
            if count_lines > conf.base_num:
                if count_lines % N != 0:
                    max_page = count_lines // N + 1
                else:
                    max_page = count_lines // N
            else:
                max_page = 1
                N = count_lines
            if current_page == max_page and current_page != 1:
                N = count_lines % ((current_page - 1) * N)
            dateold = None
            story_topup = f"<b>{adm_line}Всего операций - {count_lines}\nОперации с {(current_page - 1) * conf.base_num + 1} по {(current_page - 1) * conf.base_num + N}:</b>\n"
            while N != 0:
                if count_lines < conf.base_num:
                    num_from = N
                elif current_page != max_page:
                    num_from = current_page * conf.base_num - N + 1
                else:
                    num_from = current_page * conf.base_num - conf.base_num + N
                comm, way, sum, done, oper, time_cr = [str(x) for x in await db.get_story(user_id, num_from)]
                if oper == "withd":
                    operline = "Вывод"
                    requisites = await db.get_requisites(comm)
                    if call.data[6:11] == "toadm":
                        req_line = f"\nРеквизиты - <code>{requisites.strip()}</code>"
                    else:
                        if way == "qiwi":
                            req_line = f"\nРеквизиты - <em>+{requisites[:3]}••••{requisites[7:]}</em> \n"
                        elif way == "bank":
                            req_line = f"\nРеквизиты - <em>{requisites[:4]}••••{requisites[12:]}</em> \n"
                elif oper == "topup":
                    operline = "Пополнение"
                    req_line = "\n"
                if done == "True":
                    done = "\U00002705"
                else:
                    done = "\U0000274C"
                if way == "bank":
                    way = "Карта"
                elif way == "qiwi":
                    way = "QIWI"
                if dateold == time_cr[:10]:
                    line = f"<em>-{time_cr[11:16]}</em> - {operline} {way} - {sum}₽{req_line} (<em>№{comm} {done})</em>\n"
                if dateold != time_cr[:10]:
                    dateline = f"\n<b>• {time_cr[:10]}</b>\n"
                    line = f"{dateline}<em>-{time_cr[11:16]}</em> - {operline} {way} - {sum}₽{req_line} (<em>№{comm} {done})</em>\n"
                    dateold = time_cr[:10]
                story_topup += line
                N -= 1
            b_next = types.InlineKeyboardButton(text='\U000027A1',
                                                callback_data=f"story_{call.data[6:11]}_{format(current_page + 1, '07')}_{user_id}")
            b_back = types.InlineKeyboardButton(text='\U00002B05',
                                                callback_data=f"story_{call.data[6:11]}_{format(current_page - 1, '07')}_{user_id}")
            b_num = types.InlineKeyboardButton(text=f"{current_page}/{max_page}", callback_data=" ")
            if current_page == 1:
                if current_page == max_page:
                    buttons.append([b_num])
                else:
                    buttons.append([b_num, b_next])
            elif current_page < max_page:
                buttons.append([b_back, b_num, b_next])
            elif current_page == max_page:
                buttons.append([b_num, b_back])
            if call.data[6:11] == "toadm":
                buttons.append(
                    [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                    callback_data=f"back_adm_info_user_{user_id}")])
                buttons.append([await b().BT_AdmLk()])
            else:
                buttons.append([await b().BT_Lk()])
            await call.answer()
            await bot.edit_message_text(story_topup, call.from_user.id, call.message.message_id,
                                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                        parse_mode="HTML")


# Выбор суммы пополнения/вывода. После выбора способа пополнения/вывода.
# Запрос типа "way_тип транзакции(04)_способ(04)_откуда(04)"
@dp.callback_query(lambda call: call.data[:4] == "way_")
async def choose_sum_topup(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if call.data[10:14] == "qiwi":
            emoji = "\U0001F95D"
        elif call.data[10:14] == "bank":
            emoji = "\U0001F4B3"
        await bot.edit_message_text(f"{emoji} *Выберите желаемую сумму:*", call.from_user.id, call.message.message_id,
                                    reply_markup=await b().KB_Sum(
                                        "oper", call.data[4:9], call.data[10:14], call.data[15:19]),
                                    parse_mode="Markdown")


# Вывод информации для пополнения. После успешного создания заявки на пополнение. Запрос типа "способ(04)_topup_sum_сумма(06)"
@dp.callback_query(lambda call: call.data[4:15] == "_topup_sum_")
async def info_topup(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        way_topup = call.data[:4]
        sum_topup = call.data[15:21].lstrip("0")
        with open(f'difs/{way_topup[:1]}wallets.txt', 'r') as wallet:
            with open(f'difs/{way_topup[:1]}wallets.txt', 'r') as counter:
                max = sum(1 for line in counter) - 1
                counter.close()
            req = (wallet.readlines())[random.randint(0, max)]
            wallet.close()
        await db.topup_create(call.from_user.id, sum_topup, way_topup, req)
        get_comm = await db.get_comm(call.from_user.id, sum_topup, way_topup)
        if way_topup == "qiwi":
            url_link = "https://qiwi.com/payment/form/99"
            m_topup_create = f"{t.m_topup_create_1}<b>{sum_topup}₽</b> на QIWI кошелек <code>+{req}</code> с комментарием <b>№" \
                             f"{get_comm}</b>{t.m_topup_create_2}"
        elif way_topup == "bank":
            url_link = "https://qiwi.com/payment/form/99"
            m_topup_create = f"{t.m_topup_create_1}<b>{sum_topup}₽</b> на карту <code>{req}</code> с комментарием <b>№" \
                             f"{get_comm}</b>{t.m_topup_create_2}"
        await bot.edit_message_text(m_topup_create, call.from_user.id, call.message.message_id,
                                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                        [types.InlineKeyboardButton(text='\U0001F4B8 Оплатить', url=url_link)],
                                        [types.InlineKeyboardButton(text='\U00002705 Перевод выполнил',
                                                                    callback_data=f"check_topup_{way_topup}_{format(get_comm, '7')}")]]),
                                    parse_mode="HTML")


# Ручной ввод суммы пополнения/вывода или ставки. После выбора ручного ввода. Запрос типа "способ(04)_операция(05)_other_sum" или игра(04)_bet_other_sum
@dp.callback_query(lambda call: call.data[10:20] == "_other_sum" or call.data[4:20] == "_bet_other_sum")
async def enter_sum_topup(call, state: FSMContext):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if call.data[10:21] == "_other_sum":
            if call.data[5:10] == "withd":
                await bot.edit_message_text(f"*Введите сумму вывода:*\n\nМаксимальная сумма - *{conf.max_tw}₽*\n"
                                            f"Минимальная сумма - *{conf.min_tw}₽*\n Сумма должна быть *целым* числом (без копеек)",
                                            call.from_user.id, call.message.message_id, parse_mode="Markdown")
            else:
                await bot.edit_message_text(f"*Введите сумму пополнения:*\n\nМаксимальная сумма - *{conf.max_tw}₽*\n"
                                            f"Минимальная сумма - *{conf.min_tw}₽*\nСумма должна быть *целым* числом (без копеек)",
                                            call.from_user.id, call.message.message_id, parse_mode="Markdown")
            await state.update_data(type="oper", oper=call.data[5:10], way=call.data[:4])
        else:
            await bot.edit_message_text(f"Введите желаемую сумму ставки:\n\nМаксимальная сумма - *{conf.max_bet}₽*"
                                        f"\nМинимальная сумма - *{conf.min_bet}₽*\nСумма должна быть *целым* числом (без копеек)",
                                        call.from_user.id, call.message.message_id, parse_mode="Markdown")
            await state.update_data(type="bet", game=call.data[:4])
        await state.set_state(FSM.other_sum)


# Удаления сообщения. Запрос типа "delete_msg"
@dp.callback_query(lambda call: call.data[:11] == "delete_msg")
async def deleter(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await bot.delete_message(call.message.chat.id, call.message.message_id)


# Проверка пополнения. Запрос типа "(re)check_topup_способ(04)_айди платежа(07)"
@dp.callback_query(lambda call: call.data[:12] == "check_topup_" or call.data[:14] == "recheck_topup_")
async def check_topup(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if call.data[:12] == "check_topup_":
            N = 0
        elif call.data[:14] == "recheck_topup_":
            N = 2
        await ch().topup_checker_user(call.from_user.id, call.data[12 + N:16 + N], call.data[17 + N:24 + N].lstrip("0"),
                                      call.message.message_id)


# Создание заявки на вывод после подтверждения правильности данных. Запрос типа "confirm_with_способ(04)_сумма(06)_реквизиты(17)"
@dp.callback_query(lambda call: call.data[:13] == "confirm_with_")
async def create_withd(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        sum = call.data[18:24].lstrip("0")
        requisites = call.data[25:42].lstrip("0")
        await db.with_create(call.from_user.id, sum, call.data[13:17], requisites)
        await db.set_withdraw_balance(call.from_user.id, sum)
        m_with_create = f"\U0000267B *Ваша заявка №{await db.get_with(call.from_user.id, sum, call.data[13:17])} на сумму {sum}₽ успешно зарегистрирована*" \
                        f"\n*Указанные реквизиты - {requisites}*" \
                        f"\n\nВыполнение заявки может занимать до 24 часов"
        await bot.edit_message_text(m_with_create, call.from_user.id, call.message.message_id,
                                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[await b().BT_Lk()]]),
                                    parse_mode="Markdown")


# Проерка ставки и игры. Запрос типа "bet_игра(04)_сумма(06)"
@dp.callback_query(lambda call: call.data[:4] == "bet_")
async def check_bet(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await ch().bet_sum_checker(call)


# Изменение игры. Запрос типа "change_bet"
@dp.callback_query(lambda call: call.data[:11] == "change_bet")
async def changer_bet(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await call.message.answer("\U0001F914 Выберите тип игры",
                                  reply_markup=await b().KB_MainGames(), parse_mode="Markdown")


# Создание игровой комнаты и обработка игры. Запрос типа "create_bet_игра(04)_сумма(06)
@dp.callback_query(lambda call: call.data[:11] == "create_bet_")
async def creating_room(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await ch().bet_sum_checker(call)


# История игр
@dp.callback_query(lambda call: call.data[:12] in ("story_games_", "story_gaadm_"))
async def story_games(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await call.message.answer("*Раздел в разработке*",
                                  reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[await b().BT_Close()]),
                                  parse_mode="Markdown")


# Обработчик ручного ввода реквизитов вывода.
@dp.message(FSM.requisites)
async def user_get_requisites(message: types.Message, state: FSMContext):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        way = (await state.get_data())['way_withd']
        sum = (await state.get_data())['sum_with']
        try:
            if not message.text.isdigit():
                raise
            if ((way == "qiwi") and ((len(str(message.text)) != 11) or (message.text[:1] != "7"))) or (
                    way == "bank") and (len(message.text) != 16):
                if (way == "qiwi") and (len(str(message.text)) != 11):
                    txt_wrong = "*Неверная длина номера телефона.*\n\nНажмите на кнопку ниже и введите номер телефона еще раз"
                elif (way == "qiwi") and (message.text[:1] != "7"):
                    txt_wrong = "*Неверный номер телефона. Номер должен начинаться с 7.*\n\nНажмите на кнопку ниже и введите номер телефона еще раз"
                elif (way == "bank") and (len(message.text) != 16):
                    txt_wrong = "*Неверная длина номера карты.*\n\nНажмите на кнопку ниже и введите номер карты еще раз"
                await message.answer(txt_wrong, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                callback_data=f"{way}_withd_sum_{format(sum, '06')}")],
                    [await b().BT_Lk()]
                ]), parse_mode="Markdown")
            else:
                if way == "qiwi":
                    lineway = "QIWI"
                    req = "Номер телефона - *+"
                elif way == "bank":
                    lineway = "Карта"
                    req = "Номер карты - *"
                await message.answer("*Подтвердите правильность данных*"
                                     f"\n\nСумма - *{sum}₽*"
                                     f"\nСпособ - *{lineway}*\n{req}{message.text}*",
                                     reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                         [types.InlineKeyboardButton(text='\U00002705 Подтвердить',
                                                                     callback_data=f"confirm_with_{way}_{format(sum, '06')}_{format(message.text, '17')}")],
                                         [types.InlineKeyboardButton(text='\U0000267B Изменить',
                                                                     callback_data='withd_balance_main_')]
                                     ]), parse_mode="Markdown")
        except:
            logging.info(f"User {message.from_user.id} tried to enter requisites {message.text}")
            await message.answer("*Неверный формат реквизитов. *"
                                 "\n\nВыберите одно из действий",
                                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                     [types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                                 callback_data=f"{way}_withd_sum_{format(sum, '06')}")],
                                     [await b().BT_Lk()]
                                 ]), parse_mode="Markdown")
    await state.clear()


@dp.message(F.sticker)
async def sticker_reply(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.answer(f"<b>Спасибо за стикер\U0001F928\n"
                             f"Информация о стикере</b>\n\n"
                             f"<b>ID</b>\n<code>{message.sticker.file_id}</code>\n\n"
                             f"<b>Эмодзи</b>\n<code>{message.sticker.emoji}</code>\n\n"
                             f"<b>Анимация</b>\n{message.sticker.is_animated}\n\n"
                             f"<b>Но все же, давайте лучше сыграем!\U0001F3B0</b>",
                             reply_markup=await b().KB_Menu(), parse_mode="HTML")


@dp.message(F.dice)
async def dice_reply(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.answer(f"<b>У нас со своим нельзя\U0001F928\n"
                             f"Проверьте свою удачу у нас!</b>",
                             reply_markup=await b().KB_Menu(), parse_mode="HTML")


# Обработчик ручного ввода суммы пополнения/вывода и ставки
@dp.message(FSM.other_sum)
async def user_other_sum_enter(message, state: FSMContext):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        buttons = []
        if (await state.get_data())['type'] == "admin":
            way = (await state.get_data())['way']
            user_id = (await state.get_data())['user_id']
            if way == "add":
                lineoper = "пополнения баланса пользователя"
                text_confirm = "Пополнение баланса на "
            elif way == "rem":
                lineoper = "уменьшения баланса пользователя"
                text_confirm = "Уменьшение баланса на "
            elif way == "set":
                lineoper = ""
                text_confirm = "Новый баланс - "
            max_sum = conf.max_adm
            min_sum = conf.min_adm
            b_lk = await b().BT_AdmLk()
            b_enter_again = types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                       callback_data=f"chk_change_balance_{way}_{user_id}")
        elif (await state.get_data())['type'] == "oper":
            way = (await state.get_data())['way']
            oper = (await state.get_data())['oper']
            max_sum = conf.max_tw
            min_sum = conf.min_tw
            if oper == "withd":
                lineoper = "вывода"
            elif oper == "topup":
                lineoper = "пополнения"
            if way == "qiwi":
                lineway = "QIWI \U0001F95D"
            elif way == "bank":
                lineway = "Карта \U0001F4B3"
            b_enter_again = types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                       callback_data=f"{way}_{oper}_other_sum")
        elif (await state.get_data())['type'] == "bet":
            game = (await state.get_data())['game']
            lineoper = "ставки"
            max_sum = conf.max_bet
            min_sum = conf.min_bet
            b_enter_again = types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                       callback_data=f"{game}_bet_other_sum")
        try:
            if not message.text.isdigit():
                raise
            if (int(message.text) > max_sum) or (int(message.text) < min_sum):
                buttons.append([b_enter_again])
                buttons.append([await b().BT_Lk()])
                if int(message.text) > max_sum:
                    await message.answer(f"*Максимальная сумма {lineoper} - {max_sum}₽*"
                                         "\n\nВыберите одно из действий",
                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                         parse_mode="Markdown")
                elif int(message.text) < min_sum:
                    await message.answer(f"*Минимальная сумма {lineoper} - {min_sum}₽*"
                                         "\n\nВыберите одно из действий",
                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                         parse_mode="Markdown")
            else:
                if (await state.get_data())['type'] == "oper":
                    buttons.append([types.InlineKeyboardButton(text='\U00002705 Подтвердить',
                                                               callback_data=f"{way}_{oper}_sum_{format(int(message.text), '06')})")])
                    buttons.append([types.InlineKeyboardButton(text='\U0000267B Изменить',
                                                               callback_data=f"{oper}_balance_main_")])
                    await message.answer(f"*Подтвердите правильность способа и суммы*"
                                         f"\n\nСумма {lineoper} - *{int(message.text)}₽*"
                                         f"\nСпособ {lineoper} - *{lineway}*",
                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                         parse_mode="Markdown")
                elif (await state.get_data())['type'] == "bet":
                    await ch().bet_sum_checker(0, message.from_user.id, game, int(message.text))
                elif (await state.get_data())['type'] == "admin":
                    buttons.append([types.InlineKeyboardButton(text="\U00002705 Подтвердить",
                                                               callback_data=f"adm_change_balance_{way}_{format(int(message.text), '06')}_{user_id}")])
                    buttons.append([types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                               callback_data=f"chk_change_balance_{user_id}")])
                    await message.answer(f"<b>Подтвердите правильность данных:\n\n"
                                         f"Пользователь - <code>{user_id}</code>\n"
                                         f"{text_confirm}{message.text}₽</b>",
                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                         parse_mode="HTML")
        except:
            logging.info(
                f"User {message.from_user.id} tried to enter sum of {(await state.get_data())['type']} - {message.text}")
            buttons.append([b_enter_again])
            buttons.append([await b().BT_Lk()])
            await message.answer("*Неверный формат числа. *\n\nВыберите одно из действий",
                                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                 parse_mode="Markdown")
    await state.clear()


# Админский обработчик запроса подтверждения транзакции. Запрос типа (adm)(chk)_accure_тип транзакции(05)_
# айди транзакции
@dp.callback_query(lambda call: call.data[:11] in ("adm_accure_", "chk_accure_"))
async def change_trans_type(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        trans_type = call.data[11:16]
        trans_id = call.data[17:]
        adm_id = call.from_user.id
        if await db.adm_valid_check(adm_id):
            if await db.adm_lvl_check(adm_id) > conf.junior_lvl:
                if call.data[:3] == "adm":
                    if trans_type == "topup":
                        await db.adm_topup_true(trans_id)
                    elif trans_type == "withd":
                        await db.adm_withd_true(trans_id)
                    logging.warning(f"Admin {call.from_user.id} confirm transaction of {trans_type} №{trans_id}")
                    await bot.edit_message_text(f"*Транзакция №{trans_id} успешно подтверждена!*",
                                                adm_id, call.message.message_id,
                                                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                                    [types.InlineKeyboardButton(text='\U0000267B Другая транзакция',
                                                                                callback_data="control_transact")],
                                                    [await b().BT_AdmLk()]
                                                ]), parse_mode="Markdown")
                elif call.data[:3] == "chk":
                    if trans_type == "topup":
                        way = "пополнения"
                    elif trans_type == "withd":
                        way = "вывода"
                    await bot.edit_message_text(f"*Вы хотите подтвердить транзакцию {way} №{trans_id}?*",
                                                call.from_user.id, call.message.message_id,
                                                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                                    [types.InlineKeyboardButton(text='\U00002705 Да',
                                                                                callback_data=f"adm_accure_{trans_type}_{trans_id}")],
                                                    [await b().BT_AdmLk()]
                                                ]), parse_mode="Markdown")
            else:
                logging.warning(f"Admin {call.from_user.id} with access {await db.adm_lvl_check(adm_id)} tried to get "
                                f"access to admin functionality with call - {call}")
                await msg().no_access(adm_id, "1 (Middle)", call.message.message_id)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(adm_id, True, call.message.message_id)


# Админский обработчик с выбором типа желаемой транзакции
@dp.callback_query(lambda call: call.data == "control_transact")
async def choose_trans_type(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            await bot.edit_message_text("*Выберите тип транзакции*", call.from_user.id, call.message.message_id,
                                        parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text='Пополнение', callback_data=f"accure_topup"),
                     types.InlineKeyboardButton(text='Вывод', callback_data=f"accure_withd")],
                    [await b().BT_AdmLk("\U00002B05")]
                ]))
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)


@dp.callback_query(lambda call: call.data[:19] == "adm_change_balance_")
async def balance_change(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            if await db.adm_lvl_check(call.from_user.id) > conf.master_lvl:
                if call.data[19:22] == "nul":
                    await db.adm_nul_balance(call.data[23:])
                    await bot.edit_message_text(f"<b>Баланс пользователя <code>{call.data[23:]}</code> обнулен</b>",
                                                call.from_user.id,
                                                call.message.message_id,
                                                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                                    [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                                                callback_data=f"back_adm_info_user_{call.data[23:]}")],
                                                    [await b().BT_AdmLk()]
                                                ]), parse_mode="HTML")
                elif call.data[19:22] in ("add", "rem"):
                    if call.data[19:22] == "add":
                        await db.set_topup_balance(call.data[30:], int(call.data[23:29]))
                        text_act = "пополнен"
                    elif call.data[19:22] == "rem":
                        if int(call.data[23:29]) > await db.get_user_balance(call.data[30:]):
                            return await bot.edit_message_text(
                                f"<b>Нельзя уменьшить баланс пользователя <code>{call.data[30:]}</code> на сумму, "
                                f"превышающую его баланс - {int(await db.get_user_balance(call.data[30:]))}₽</b>",
                                call.from_user.id, call.message.message_id,
                                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                    [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                                callback_data=f"chk_change_balance_{call.data[30:]}")],
                                    [await b().BT_AdmLk()]
                                ]), parse_mode="HTML")
                        else:
                            await db.set_withdraw_balance(call.data[30:], int(call.data[23:29]))
                            text_act = "уменьшен"
                    await bot.edit_message_text(
                        f"<b>Баланс пользователя <code>{call.data[30:]}</code> {text_act} на {int(call.data[23:29])}₽</b>",
                        call.from_user.id, call.message.message_id, reply_markup=
                        types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                        callback_data=f"back_adm_info_user_{call.data[30:]}")],
                            [await b().BT_AdmLk()]
                        ]), parse_mode="HTML")
                elif call.data[19:22] == "set":
                    await db.adm_set_balance(call.data[30:], int(call.data[23:29]))
                    await bot.edit_message_text(
                        f"<b>Новый баланс пользователя <code>{call.data[30:]}</code> - {int(call.data[23:29])}₽</b>",
                        call.from_user.id,
                        call.message.message_id, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                        callback_data=f"back_adm_info_user_{call.data[30:]}")],
                            [await b().BT_AdmLk()]
                        ]), parse_mode="HTML")
            else:
                await msg().no_access(call.from_user.id, "3 (Superuser)", call.message.message_id)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)


@dp.callback_query(lambda call: call.data[:19] == "chk_change_balance_")
async def balance_change_check(call, state: FSMContext):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            if await db.adm_lvl_check(call.from_user.id) > conf.master_lvl:
                if call.data[19:22] not in ("add", "rem", "nul", "set"):
                    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                        [
                            types.InlineKeyboardButton(text="\U0001F4C8 Добавить",
                                                       callback_data=f"chk_change_balance_add_{call.data[19:]}"),
                            types.InlineKeyboardButton(text="\U0001F4C9 Снять",
                                                       callback_data=f"chk_change_balance_rem_{call.data[19:]}")],
                        [
                            types.InlineKeyboardButton(text="\U0001F4A3 Обнулить",
                                                       callback_data=f"chk_change_balance_nul_{call.data[19:]}"),
                            types.InlineKeyboardButton(text="\U0001F4DD Изменить",
                                                       callback_data=f"chk_change_balance_set_{call.data[19:]}")
                        ],
                        [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                    callback_data=f"back_adm_info_user_{call.data[19:]}")],
                        [await b().BT_AdmLk()]
                    ])
                    await bot.edit_message_text(
                        f"<b>Выберите действие с балансом пользователя <code>{call.data[19:]}</code></b>",
                        call.from_user.id,
                        call.message.message_id, reply_markup=keyboard, parse_mode="HTML")
                else:
                    if call.data[19:22] in ("add", "rem"):
                        if call.data[28:29] != "_":
                            if call.data[19:22] == "add":
                                text_act = "увеличения"
                            else:
                                text_act = "уменьшения"
                            await bot.edit_message_text(
                                f"<b>Выберите сумму {text_act} баланса пользователя <code>{call.data[23:]}</code></b>",
                                call.from_user.id, call.message.message_id,
                                reply_markup=await b().KB_Sum("admin", call.data[23:], call.data[19:22]),
                                parse_mode="HTML")
                        else:
                            if call.data[19:22] == "add":
                                text_act = "добавления"
                            else:
                                text_act = "уменьшения"
                            await bot.edit_message_text(
                                f"<b>Введите сумму {text_act} баланса пользователя <code>{call.data[29:]}</code></b>",
                                call.from_user.id,
                                call.message.message_id, parse_mode="HTML")
                            await state.update_data(type="admin", way=call.data[19:22], user_id=call.data[29:])
                            await state.set_state(FSM.other_sum)
                    elif call.data[19:22] == "nul":
                        await bot.edit_message_text(
                            f"<b>Вы действительно хотите обнулить баланс пользователя <code>{call.data[23:]}</code>?</b>",
                            call.from_user.id,
                            call.message.message_id, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                [types.InlineKeyboardButton(text="\U0001F512 Да",
                                                            callback_data=f"adm_change_balance_nul_{call.data[23:]}")],
                                [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                            callback_data=f"chk_change_balance_{call.data[23:]}")],
                                [await b().BT_AdmLk()]
                            ]), parse_mode="HTML")
                    elif call.data[19:22] == "set":
                        await bot.edit_message_text(
                            f"<b>Введите новый баланс пользователя <code>{call.data[23:]}</code></b>",
                            call.from_user.id,
                            call.message.message_id, parse_mode="HTML")
                        await state.update_data(type="admin", way="set", user_id=call.data[23:])
                        await state.set_state(FSM.other_sum)
            else:
                await msg().no_access(call.from_user.id, "3 (Superuser)", call.message.message_id)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)


@dp.callback_query(lambda call: call.data == "control_users")
async def enter_user(call, state: FSMContext):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            await bot.edit_message_text("*Введите ник или айди пользователя*", call.from_user.id,
                                        call.message.message_id, parse_mode="Markdown")
            await state.update_data(id_adm=call.from_user.id)
            await state.set_state(FSM.enter_id_user)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)


@dp.callback_query(lambda call: call.data[:15] == "chk_block_user_")
async def check_block_user(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
                if await db.get_ban(call.data[15:]):
                    text_act = "разблокировать"
                else:
                    text_act = "заблокировать"
                await bot.edit_message_text(
                    f"<b>Вы действительно хотите {text_act} пользователя <code>{call.data[15:]}</code>?</b>",
                    call.from_user.id, call.message.message_id,
                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                        [types.InlineKeyboardButton(text="\U0001F512 Да",
                                                    callback_data=f"adm_block_user_{call.data[15:]}")],
                        [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                    callback_data=f"back_adm_info_user_{call.data[15:]}")],
                        [await b().BT_AdmLk()]
                    ]), parse_mode="HTML")
            else:
                await msg().no_access(call.from_user.id, "2 (Master)", call.message.message_id)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)


@dp.callback_query(lambda call: call.data[:15] == "adm_block_user_")
async def block_user(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
                if await db.get_ban(call.data[15:]):
                    action = False
                    text_act = "разблокирован"
                else:
                    action = True
                    text_act = "заблокирован"
                await db.adm_ban_user(call.data[15:], action)
                await bot.edit_message_text(f"<b>Пользователь <code>{call.data[15:]}</code> успешно {text_act}!</b>",
                                            call.from_user.id, call.message.message_id, reply_markup=
                                            types.InlineKeyboardMarkup(inline_keyboard=[
                                                [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                                            callback_data=f"back_adm_info_user_{call.data[15:]}")],
                                                [await b().BT_AdmLk()]
                                            ]), parse_mode="HTML")
            else:
                await msg().no_access(call.from_user.id, "2 (Master)", call.message.message_id)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)


@dp.callback_query(lambda call: call.data[:19] == "back_adm_info_user_")
async def user_info(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            await adm_user_info(call.from_user.id, call.data[19:], False, call.message.message_id)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with message - {call.from_user.id}")
            await msg().adm_no_valid(call.from_user.id, True)


async def adm_user_info(adm_id, user_id, send, msg_id=""):
    if await ch().rules_checker(adm_id) == (True, False):
        if await db.adm_valid_check(adm_id):
            if user_id.isdigit() and await db.get_user_exists(user_id) or await db.get_user_exists(user_id,
                                                                                                   "username ILIKE"):
                if user_id.isdigit():
                    key = "user_id ="
                else:
                    key = "username ILIKE"
                id_sys, user_id, join_date, balance, name, lastname, username, rules_acc, ban = [x for x in
                                                                                                 await db.adm_user_info(
                                                                                                     user_id, key)]
                join_date = str(join_date)
                buttons = [
                    [types.InlineKeyboardButton(text="Операции", callback_data=f"story_toadm_0000001_{user_id}"),
                    types.InlineKeyboardButton(text="Игры", callback_data=f"story_gaadm_0000001_{user_id}")]
                ]
                if lastname is not None:
                    lastname_info = f"\nВторое имя - {lastname}\n"
                else:
                    lastname_info = "\n"
                if rules_acc:
                    rules_info = "\U00002705"
                else:
                    rules_info = "\U0000274C"
                if ban:
                    ban_info = "Присутствует \U0001F4DB"
                else:
                    ban_info = "Отсутствует \U0000274E"
                if await db.adm_lvl_check(adm_id) > conf.junior_lvl:
                    buttons.append([types.InlineKeyboardButton(text="\U00002754 Проверить",
                                                               callback_data=f"adm_check_user_{user_id}")])
                    if await db.adm_lvl_check(adm_id) > conf.middle_lvl:
                        if await db.get_ban(user_id):
                            text_act = "\U0000274E Разблокировать"
                        else:
                            text_act = "\U0000274C Заблокировать"
                        buttons.append(
                            [types.InlineKeyboardButton(text=text_act, callback_data=f"chk_block_user_{user_id}")])
                        if await db.adm_lvl_check(adm_id) > conf.master_lvl:
                            buttons.append([types.InlineKeyboardButton(text="\U0001F4DD Изменить баланс",
                                                                       callback_data=f"chk_change_balance_{user_id}")])
                buttons.append([types.InlineKeyboardButton(text="\U0000267B Другой пользователь",
                                                           callback_data="control_users")])
                buttons.append([await b().BT_AdmLk()])
                if send:
                    await bot.send_message(adm_id, f"<b>Данные о пользователе:\n\nID - </b><code>{user_id}</code>\n"
                                                   f"<b>Имя -</b> {name}{lastname_info}<b>Баланс -</b> {format(balance, '.0f')}₽\n"
                                                   f"<b>Дата регистрации -</b> {join_date[:10]}\n<b>Правила - {rules_info}\n"
                                                   f"Наличие бана - {ban_info}</b>",
                                           reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                           parse_mode="HTML")
                else:
                    await bot.edit_message_text(f"<b>Данные о пользователе:\n\nID - </b><code>{user_id}</code>\n"
                                                f"<b>Имя -</b> {name}{lastname_info}<b>Баланс -</b> {format(balance, '.0f')}₽\n"
                                                f"<b>Дата регистрации -</b> {join_date[:10]}\n<b>Правила - {rules_info}\n"
                                                f"Наличие бана - {ban_info}</b>", adm_id, msg_id,
                                                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                                parse_mode="HTML")
            else:
                await bot.send_message(adm_id, "*Данный пользователь не найден*",
                                       reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                           [types.InlineKeyboardButton(text="\U0000267B Ввести заново",
                                                                       callback_data="control_users")],
                                           [await b().BT_AdmLk()]
                                       ]), parse_mode="Markdown")
        else:
            logging.warning(f"Not valid admin {adm_id} tried to get access to admin panel with message - {user_id}")
            await msg().adm_no_valid(adm_id, True)


@dp.message(FSM.enter_id_user)
async def get_id_trans(message: types.Message, state: FSMContext):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        adm_id = (await state.get_data())['id_adm']
        if await db.adm_valid_check(adm_id):
            await adm_user_info(adm_id, message.text, True)
        else:
            logging.warning(f"Not valid admin {adm_id} tried to get access to admin panel with message - {message}")
            await msg().adm_no_valid(adm_id, True)
    await state.clear()


# Админский обработчик ручного ввода номера транзакции. Запрос типа accure_тип транзакции(05)
@dp.callback_query(lambda call: call.data[:7] == "accure_")
async def accure_trans(call, state: FSMContext):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            if call.data[7:12] == "topup":
                await bot.edit_message_text("*Введите ID пополнения*", call.from_user.id, call.message.message_id,
                                            parse_mode="Markdown")
            elif call.data[7:12] == "withd":
                await bot.edit_message_text("*Введите ID вывода*", call.from_user.id, call.message.message_id,
                                            parse_mode="Markdown")
            await state.update_data(id_adm=call.from_user.id, trans_type=call.data[7:12])
            await state.set_state(FSM.accure_id_trans)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)


# Админский обработчик подтверждения смены способа вывода. Запрос типа chk_withd_change_way_айди вывода
@dp.callback_query(lambda call: call.data[:21] == "chk_withd_change_way_")
async def change_withd_way(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
                if await db.get_withd_way(call.data[21:]) == "bank":
                    button_another_way = types.InlineKeyboardButton(text="QIWI",
                                                                    callback_data=f"rqs_withd_change_qiwi_{call.data[21:]}")
                    way_withd_write = "Банковская карта"
                elif await db.get_withd_way(call.data[21:]) == "qiwi":
                    button_another_way = types.InlineKeyboardButton(text="Банковская карта",
                                                                    callback_data=f"rqs_withd_change_bank_{call.data[21:]}")
                    way_withd_write = "QIWI"
                await bot.edit_message_text(f"*Текущий способ вывода транзакции №{call.data[21:]} - {way_withd_write}"
                                            "\n\nВозможность изменить способ вывода на:*", call.from_user.id,
                                            call.message.message_id,
                                            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                                [button_another_way],
                                                [await b().BT_AdmLk()]
                                            ]), parse_mode="Markdown")
            else:
                logging.warning(
                    f"Admin {call.from_user.id} with access {await db.adm_lvl_check(call.from_user.id)} tried to get "
                    f"access to admin functionality with call - {call}")
                await msg().no_access(call.from_user.id, "2 (Master)", call.message.message_id)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)


# Админский обработчик ручного ввода новых реквизитов. Запрос типа rqs_withd_change_способ вывода(04)_старый способ(04)
@dp.callback_query(lambda call: call.data[:17] == "rqs_withd_change_")
async def get_new_req(call, state: FSMContext):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
                await bot.edit_message_text("*Введите новые реквизиты*", call.from_user.id, call.message.message_id,
                                            parse_mode="Markdown")
                await state.update_data(id_adm=call.from_user.id, new_way=call.data[17:21],
                                        old_way=await db.get_withd_way(call.data[22:]), with_id=call.data[22:])
                await state.set_state(FSM.adm_new_requis)
            else:
                logging.warning(
                    f"Admin {call.from_user.id} with access {await db.adm_lvl_check(call.from_user.id)} tried to get "
                    f"access to admin functionality with call - {call}")
                await msg().no_access(call.from_user.id, "2 (Master)", call.message.message_id)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, True, call.message.message_id)


# Админская панель отображения измененных данных вывода
@dp.message(FSM.adm_new_requis)
async def get_id_trans(message: types.Message, state: FSMContext):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        data = await state.get_data()
        buttons = []
        adm_id = data['id_adm']
        with_id = int(data['with_id'])
        if await db.adm_valid_check(adm_id):
            if await db.adm_lvl_check(adm_id) > conf.middle_lvl:
                try:
                    if not message.text.isdigit():
                        raise
                    new_req = int(message.text)
                    if data['new_way'] == "bank":
                        if len(str(new_req)) != 16:
                            raise
                        new_way_w = "Банковская карта"
                    elif data['new_way'] == "qiwi":
                        if len(str(new_req)) != 11 or str(new_req)[0] != "7":
                            raise
                        new_way_w = "QIWI"
                    if data['new_way'] != data['old_way']:
                        about_new_way = f"Новый способ - {new_way_w}\n"
                    else:
                        about_new_way = ""
                    buttons.append([types.InlineKeyboardButton(text="\U00002705 Подтвердить",
                                                               callback_data=f"adm_withd_change_{data['new_way']}_{format(with_id, '010')}_{new_req}")])
                    buttons.append([await b().BT_AdmLk()])
                    await message.answer(f"*Желаемые изменения: \n\nТранзакция №{with_id}\n"
                                         f"{about_new_way}Новые реквизиты - {new_req}*",
                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                         parse_mode="Markdown")
                except:
                    buttons.append([types.InlineKeyboardButton(text="\U0000267B Ввести заново",
                                                               callback_data=f"rqs_withd_change_{data['new_way']}_{with_id}")])
                    buttons.append([await b().BT_AdmLk()])
                    await message.answer("*Неверные реквизиты\n\nВыберите одно из действий:*",
                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons),
                                         parse_mode="Markdown")
            else:
                logging.warning(
                    f"Admin {message.from_user.id} with access {await db.adm_lvl_check(adm_id)} tried to get "
                    f"access to admin functionality with message - {message}")
                await msg().no_access(adm_id, "2 (Master)")
        else:
            logging.warning(
                f"Not valid admin {message.from_user.id} tried to get access to admin panel with call - {message}")
            await msg().adm_no_valid(adm_id, False)
    await state.clear()


# Админский обработчик изменения транзакции вывода. Запрос типа adm_withd_change_способ(04)_
# айди транзакции(10)_новые реквизиты
@dp.callback_query(lambda call: call.data[:17] == "adm_withd_change_")
async def change_withd_way(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if await db.adm_valid_check(call.from_user.id):
            if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
                logging.warning(
                    f"Admin {call.from_user.id} change requisites from {await db.get_requisites(call.data[22:32].lstrip('0'))} to {call.data[33:]}")
                await db.adm_update_withd(call.data[22:32].lstrip("0"), call.data[17:21], call.data[33:])
                if call.data[17:21] == "bank":
                    new_way_w = "Банковская карта"
                else:
                    new_way_w = "QIWI"
                await bot.edit_message_text(
                    f"*Текущая информация: \n\nТранзакция №{call.data[22:32].lstrip('0')}\nСпособ - {new_way_w}"
                    f"\nРеквизиты - {call.data[33:]}*", call.from_user.id,
                    call.message.message_id, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                        [types.InlineKeyboardButton(text='\U0000267B Другая транзакция',
                                                    callback_data="control_transact")],
                        [await b().BT_AdmLk()]
                    ]), parse_mode="Markdown")
            else:
                logging.warning(
                    f"Admin {call.from_user.id} with access {await db.adm_lvl_check(call.from_user.id)} tried to get "
                    f"access to admin functionality with call - {call}")
                await msg().no_access(call.from_user.id, "2 (Master)", call.message.message_id)
        else:
            logging.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            await msg().adm_no_valid(call.from_user.id, False)


# Админская панель отображения транзакций
@dp.message(FSM.accure_id_trans)
async def get_id_trans(message: types.Message, state: FSMContext):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        data = await state.get_data()
        buttons = []
        id_adm = data['id_adm']
        trans_type = data['trans_type']
        b_adm_trans = types.InlineKeyboardButton(text='\U0000267B Другая транзакция',
                                                 callback_data="control_transact")
        try:
            if not message.text.isdigit():
                raise
            if await db.adm_valid_check(id_adm):
                if 0 < int(message.text) < 100000:
                    if trans_type == "topup":
                        id_get_trans, user, way, sum, time_cr, accure, done, time_do, oper, requisites = [str(x) for x in
                                                                                              await db.adm_info_topup(
                                                                                                  message.text)]
                        if accure == "False":
                            accure_w = "\U0000274C"
                        else:
                            accure_w = "\U00002705"
                    elif trans_type == "withd":
                        id_get_trans, user, way, sum, time_cr, done, time_do, oper, requisites = [str(x) for x in
                                                                                                  await db.adm_info_withd(
                                                                                                      message.text)]
                    if way == "qiwi":
                        way_w = "QIWI"
                    elif way == "bank":
                        way_w = "Банковская карта"
                    if done == "False":
                        done_w = "\U0000274C"
                    else:
                        done_w = "\U00002705"
                    if time_do == "None":
                        time_do_w = "\U0000274C"
                    else:
                        time_do_w = time_do
                    username = str(await db.adm_find_username(user))
                    if username == "None":
                        username = "Никнейм отсуствует"
                    else:
                        username = f"@{username}"
                    if trans_type == "topup":
                        if accure == "False" and await db.adm_lvl_check(id_adm) > conf.junior_lvl:
                            buttons.append([types.InlineKeyboardButton(text='\U00002705 Подтвердить транзакцию',
                                                                    callback_data=f"chk_accure_topup_{id_get_trans}")])
                        buttons.append([b_adm_trans])
                        buttons.append([await b().BT_AdmLk()])
                        await message.answer(f"Транзакция №{id_get_trans}"
                                             f"\nПользователь - {username} (id<code>{user}</code>)"
                                             f"\nСпособ - {way_w}"
                                             f"\nСумма - {sum} ₽"
                                             f"\nВремя создания - {time_cr}"
                                             f"\nПеревод выполнен - {accure_w}"
                                             f"\nПополнение завершено - {done_w}"
                                             f"\nВремя завершения - {time_do_w}",
                                             reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
                    elif trans_type == "withd":
                        if done == "False" and await db.adm_lvl_check(id_adm) > conf.junior_lvl:
                            buttons.append([types.InlineKeyboardButton(text='\U00002705 Подтвердить транзакцию',
                                                                    callback_data=f"chk_accure_withd_{id_get_trans}")])
                            if await db.adm_lvl_check(id_adm) > conf.middle_lvl:
                                buttons.append([types.InlineKeyboardButton(text='\U0000267B Изменить способ',
                                                                        callback_data=f"chk_withd_change_way_{id_get_trans}")])
                                buttons.append([types.InlineKeyboardButton(text='\U0000267B Изменить реквизиты',
                                                                        callback_data=f"rqs_withd_change_{way}_{id_get_trans}")])
                        buttons.append([b_adm_trans])
                        buttons.append([await b().BT_AdmLk()])
                        await message.answer(f"Транзакция №{id_get_trans}"
                                             f"\nПользователь - {username} (id<code>{user}</code>)"
                                             f"\nСпособ - {way_w}"
                                             f"\nСумма - {sum} ₽"
                                             f"\nВремя создания - {time_cr}"
                                             f"\nВывод завершен - {done_w}"
                                             f"\nВремя завершения - {time_do_w}"
                                             f"\nРеквизиты - <code>{requisites}</code>",
                                             reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
                else:
                    raise
            else:
                logging.warning(
                    f"Not valid admin {message.from_user.id} tried to get access to admin panel with call - {message}")
                await msg().adm_no_valid(id_adm, False)
        except:
            buttons.append([b_adm_trans])
            buttons.append([await b().BT_AdmLk()])
            await message.answer(f"*Транзакция с таким номером не найдена.*"
                                 "\n\nВыберите одно из действий",
                                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")
    await state.clear()


@dp.message(lambda message: message.text == "\U0001F464 Личный кабинет")
async def account(message):
    await ch().data_checker(message.from_user)
    if await ch().rules_checker(message.from_user.id) == (True, False):
        text, keyboard = await b().KBT_Account(message.from_user.id)
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@dp.message(lambda message: message.text == "\U0001F4AC Поддержка")
async def main_rules(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.delete()
        await message.answer("\U00002139 В случае возникновения проблем с использованием "
                             "бота вы можете связаться с поддержкой используя кнопку ниже:",
                             reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                 [await b().BT_Support()],
                                 [await b().BT_Close()]
                             ]), parse_mode="Markdown")


@dp.message(lambda message: message.text == "\U0001F4D5 Правила")
async def main_new_rules(message):
    await message.delete()
    await message.answer(t.m_rules, parse_mode="Markdown")


@dp.message(lambda message: message.text == "\U00002705 Принять правила")
async def main_start(message):
    await message.answer("Теперь вы можете воспользоваться нашим ботом", reply_markup=await b().KB_Start())
    await db.set_rules_accept(message.from_user.id)


@dp.message(lambda message: message.text in ("\U00002139 Меню", "\U00002B05 В меню", "\U0001F680 Начать пользование"))
async def main(message: types.Message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.answer("\U0001F4CD Вы перешли в меню",
                             reply_markup=await b().KB_Menu(), parse_mode="Markdown")


@dp.message(lambda message: message.text in ("\U0001F3AE Игры", "\U00002B05 К играм", "\U00002B05 Назад"))
async def main_games(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.answer("\U0001F914 Выберите тип игры",
                             reply_markup=await b().KB_MainGames(), parse_mode="Markdown")


@dp.message(lambda message: message.text in ("\U0001F4BB Онлайн"))
async def main_games(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.answer("\U0001F3AF Выберите игру",
                             reply_markup=await b().KB_OnlineGames(), parse_mode="Markdown")


@dp.message(lambda message: message.text in ("\U0001F680 Быстрая игра"))
async def main_games(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.answer("\U0001F3AF Выберите игру",
                             reply_markup=await b().KB_OfflineGames(), parse_mode="Markdown")


@dp.message(lambda message: message.text == "\U00002139 Справка")
async def info_bot(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.answer(t.m_main_info,
                             reply_markup=await b().KB_Info(), parse_mode="Markdown")


@dp.message(lambda message: message.text in ("\U0001F4AC Комиссия", "\U0001F4AC Алгоритмы", "\U0001F4AC Правила"))
async def que_answ(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.delete()
        await message.answer(t.dct_que_answ[message.text],
                             reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[await b().BT_Close()]), parse_mode="Markdown")


@dp.message(lambda message: message.text in ("\U0001F93A Дуэль", "\U0001F3B2 Русская рулетка",
                                             "\U0001F451 Королевская битва", "\U0001F3B3 Боулинг",
                                             "\U0001F3B2 Бросить кубик", "\U0001F3B0 Крутить рулетку"))
async def online_game_bet(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        text, keyboard = await b().KBT_GameBet(message.text)
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@dp.message()
async def uni_reply(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        if message.forward_from:
            if message.forward_from.username:
                nickname = message.forward_from.username
            else:
                nickname = "Отсутствует"
            if message.forward_from.is_bot:
                text_user = "бота"
            else:
                text_user = "пользователя"
            if await db.get_user_exists(message.forward_from.id) and await db.adm_check(
                    message.from_user.id) and await db.adm_valid_check(message.from_user.id):
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                    types.InlineKeyboardButton(text="\U0001F4D6 Информация о пользователе",
                                              callback_data=f"back_adm_info_user_{message.forward_from.id}")
                ])
            else:
                keyboard = await b().KB_Menu()
            await message.answer(f"<b>Пересланное сообщение от {text_user}</b>\n\n"
                                 f"<b>ID {text_user} - </b><code>{message.forward_from.id}</code>\n"
                                 f"<b>Имя {text_user} - </b>{message.forward_from.first_name}\n"
                                 f"<b>Никнейм - </b><code>{nickname}</code>",
                                 reply_markup=keyboard, parse_mode="HTML")
        elif message.forward_from_chat:
            await message.answer(f"<b>Пересланное сообщение из канала</b>\n\n"
                                 f"<b>ID чата - </b><code>{message.forward_from_chat.id}</code>\n"
                                 f"<b>Название чата - </b>{message.forward_from_chat.title}",
                                 reply_markup=await b().KB_Menu(), parse_mode="HTML")
        elif message.forward_sender_name:
            await message.answer(
                f"<b>Пользователь запретил доступ к собственной информации настройками приватности</b>",
                reply_markup=await b().KB_Menu(), parse_mode="HTML")


async def main():
    if conf.ch_start:
        asyncio.gather(ch().topup_cheker_all(), ch().winner_warned_checker())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
