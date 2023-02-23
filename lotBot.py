import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
import conf
from db import BotDB
from texts import TextsTg as t
from buttonsTg import ButtonsTg as b
from fsm import FSM
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from checkers import Checkers as ch


db = BotDB('lotEasy.db')
bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
print("\nBot successfully started!")
asyncio.gather(ch().topupChekerAll(), ch().winnerWarnedChecker())


#Запуск бота
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if not await db.user_exists(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name,
                          message.from_user.last_name, message.from_user.username)
        await b().ButtonRulesAccept(message.from_user.id, True)
    await ch().data_checker(message.from_user)
    if await db.get_rules_accept(message.from_user.id) == 0:
        await b().ButtonRulesAccept(message.from_user.id, False)
    else:
        await b().ButtonNotNew(message.from_user.id)

#Вызов основной админской панели BPManager через команду
@dp.message_handler(commands=['bpm'])
async def adm_manage(message: types.Message):
    if await db.adm_check(message.from_user.id):
        if await db.adm_valid_check(message.from_user.id):
            text, keyboard = await b().bpmanag_main(message.from_user.id)
            await bot.send_message(message.from_user.id, text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await b().bpmanag_no_valid(message.from_user.id, False)
    else:
        await b().bpmanag_no(message.from_user.id)


#Вызов основной админской панели BPManager через callback. Запрос типа main_bpmanag
@dp.callback_query_handler(lambda call: call.data[:13] == "main_bpmanag")
async def way_topup(call):
    if await db.adm_check(call.from_user.id):
        if await db.adm_valid_check(call.from_user.id):
            text, keyboard = await b().bpmanag_main(call.from_user.id)
            await bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await b().bpmanag_no_valid(call.from_user.id, True, call.message.message_id)
    else:
        await b().bpmanag_no(call.from_user.id)


#Выбор способа пополнения/вывода баланса. Запрос типа "тип транзакции(05)_balance_откуда перенаправило(04)"
@dp.callback_query_handler(lambda call: call.data[5:14] == "_balance_")
async def way_tw(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        way = call.data[14:18]
        keyboard = types.InlineKeyboardMarkup(2)
        if way == "main":
            b_back = await b().button_lk("\U00002B05")
        elif way in ("king", "duel", "russ"):
            b_back = types.InlineKeyboardButton('\U00002B05 Назад', callback_data=f"back_to_game_{way}")
        keyboard.add(types.InlineKeyboardButton('\U0001F95D QIWI',
                                                    callback_data=f"way_{call.data[:5]}_qiwi_{way}"),
                     types.InlineKeyboardButton('\U0001F4B3 Карта',
                                                callback_data=f"way_{call.data[:5]}_bank_{way}")
                     )
        keyboard.row(b_back)
        await bot.edit_message_text(t.dct_type_way[call.data[:5]], call.from_user.id, call.message.message_id,
                                    reply_markup=keyboard, parse_mode="Markdown")


#Возвращения в аккаунт. Запрос типа "back_to_acc"
@dp.callback_query_handler(lambda call: call.data[:12] == "back_to_acc")
async def back_acc(call):
    await ch().data_checker(call.from_user)
    if await ch().rules_checker(call.from_user.id) == (True, False):
        text, keyboard = await b().ButtonAccount(call.from_user.id)
        await bot.edit_message_text(text, call.from_user.id, call.message.message_id,
                                    reply_markup=keyboard, parse_mode="Markdown")


#Ввод реквизитов вывода. Проверка возможности вывода введенной суммы. Запрос типа "способ(04)_withd_sum_сумма(06)"
@dp.callback_query_handler(lambda call: call.data[4:15] == "_withd_sum_")
async def enter_req(call, state: FSMContext):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        way_withd = call.data[:4]
        sum_with = int(call.data[15:21].lstrip("0"))
        if sum_with <= await db.get_user_balance(call.from_user.id):
            await bot.edit_message_text(t.dct_enter_req[way_withd], call.from_user.id, call.message.message_id, parse_mode="Markdown")
            await state.update_data(way_withd=way_withd, sum_with=sum_with)
            await FSM.requisites.set()
        elif sum_with > await db.get_user_balance(call.from_user.id):
            m_no_money = f"\U0000274C *Недостаточно средств на балансе для вывода {sum_with}₽"\
                         f"\n\nВаш баланс: {await db.get_user_balance(call.from_user.id)}₽*\n\nПопробуйте выбрать другую сумму"
            await bot.edit_message_text(m_no_money, call.from_user.id, call.message.message_id,
                                        reply_markup=types.InlineKeyboardMarkup(1).add(await b().button_lk()),
                                        parse_mode="Markdown")


#Вывод справок об играх. Из главного меню. Запрос типа "que_тип игры(04)"
@dp.callback_query_handler(lambda call: call.data[:4] == "que_")
async def info_games(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await bot.edit_message_text(t.dct_games_que[call.data[4:8]], call.from_user.id, call.message.message_id,
                                    reply_markup=types.InlineKeyboardMarkup().add(
                                        types.InlineKeyboardButton('\U00002B05 Назад',
                                                                   callback_data=f"back_to_game_{call.data[4:8]}")),
                                    parse_mode="Markdown")


#Назад к играм. Запрос типа "back_to_game_игра(04)"
@dp.callback_query_handler(lambda call: call.data[:13] == "back_to_game_")
async def back_games(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        text, keyboard = await b().KBT_GameBet(call.data[13:17])
        await bot.edit_message_text(text, call.from_user.id, call.message.message_id, reply_markup=keyboard, parse_mode="Markdown")


#Вывод списка операций. Переход из ЛК или выбора отображения всех операций. Запрос типа "story_topup_количество(0 - 10 шт, 1 - все)"
@dp.callback_query_handler(lambda call: call.data[:12] == "story_topup_")
async def story_oper(call):
    user_id = call.from_user.id
    if await ch().rules_checker(user_id) == (True, False):
        N = conf.base_num
        count_lines = await db.get_topup_lines(user_id) + await db.get_withd_lines(user_id)
        keyboard = types.InlineKeyboardMarkup()
        if count_lines == 0:
            keyboard.add(await b().button_close())
            await bot.send_message(user_id, "У вас пока что нет операций", reply_markup=keyboard, parse_mode="Markdown")
        else:
            if (call.data[:14] == "story_topup_1") or (count_lines < N):
                N = count_lines
            elif (call.data[:14] == "story_topup_1") and (count_lines > conf.extended_num):
                N = conf.extended_num
            time_cr = str((await db.get_story(user_id, N))[5])
            dateline = f"*• {time_cr[:10]}*\n"
            dateold = time_cr[:10]
            story_topup = f"*Последние {N} операций:*\n\n{dateline}"
            if count_lines < N:
                story_topup = f"*Отображены последние {N} операций:*\n\n{dateline}"
            elif (call.data[:14] == "story_topup_1") and (count_lines > 20):
                N = 20
                story_topup = f"*Слишком много операций.\nОтображены последние {N} операций:*\n\n"
            while N != 0:
                comm, way, sum, done, oper, time_cr = [str(x) for x in await db.get_story(user_id, N)]
                if oper == "Вывод":
                    requisites = str(await db.get_requisites(comm)).strip(" ")
                    if len(requisites) == 11:
                        req_line = f"\nРеквизиты - _+{requisites[:3]}••••{requisites[7:]}_ \n"
                    elif len(requisites) == 16:
                        req_line = f"\nРеквизиты - _{requisites[:4]}••••{requisites[12:]}_ \n"
                else:
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
                    line = f"_-{time_cr[11:16]}_ - {oper} {way} - {sum}₽{req_line} (_№{comm} {done})_\n"
                if dateold != time_cr[:10]:
                    dateline = f"\n*• {time_cr[:10]}*\n"
                    line = f"{dateline}_-{time_cr[11:16]}_ - {oper} {way} - {sum}₽{req_line} (_№{comm} {done})_\n"
                    dateold = time_cr[:10]
                story_topup += line
                N-=1
            if call.data[:13] == "story_topup_1":
                keyboard.add(await b().button_close())
                await bot.edit_message_text(story_topup, user_id, call.message.message_id, reply_markup=keyboard, parse_mode="Markdown")
            if call.data[:13] == "story_topup_0":
                keyboard.add(types.InlineKeyboardButton('Показать все', callback_data=f"story_topup_1"), await b().button_close())
                await bot.send_message(user_id, story_topup, reply_markup=keyboard, parse_mode="Markdown")


# Выбор суммы пополнения/вывода. После выбора способа пополнения/вывода.
# Запрос типа "way_тип транзакции(04)_способ(04)_откуда(04)"
@dp.callback_query_handler(lambda call: call.data[:4] == "way_")
async def choose_sum_topup(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        type = call.data[4:9]
        keyboard = types.InlineKeyboardMarkup(2)
        way = call.data[10:14]

        async def button_sum(emoji, sum):
            return types.InlineKeyboardButton(f"{emoji} {sum} ₽",
                                                  callback_data=f"{way}_{type}_sum_{format(sum, '06')}")
        b_50 = await button_sum("\U0001F4B4", 50)
        b_100 = await button_sum("\U0001F4B5", 100)
        b_500 = await button_sum("\U0001F4B6", 500)
        b_1000 = await button_sum("\U0001F4B0", 1000)
        b_other = types.InlineKeyboardButton('\U0001F4DD Другая сумма',
                                                     callback_data=f"{way}_{type}_other_sum")
        b_other_way = types.InlineKeyboardButton('\U00002B05 Назад',
                                                   callback_data=f"{type}_balance_{call.data[15:19]}")
        keyboard.add(b_50, b_100, b_500, b_1000, b_other)
        keyboard.row(b_other_way)
        if way == "qiwi":
            await bot.edit_message_text(t.m_choose_qiwi_sum, call.from_user.id, call.message.message_id,
                                              reply_markup=keyboard, parse_mode="Markdown")
        elif way == "bank":
            await bot.edit_message_text(t.m_choose_bank_sum, call.from_user.id, call.message.message_id,
                                              reply_markup=keyboard, parse_mode="Markdown")


# Вывод информации для пополнения. После успешного создания заявки на пополнение. Запрос типа "способ(04)_topup_sum_сумма(06)"
@dp.callback_query_handler(lambda call: call.data[4:15] == "_topup_sum_")
async def info_topup(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        way_topup = call.data[:4]
        sum_topup = call.data[15:21].lstrip("0")
        await db.topup_create(call.from_user.id, sum_topup, way_topup)
        get_comm = await db.get_comm(call.from_user.id, sum_topup, way_topup)
        if way_topup == "qiwi":
            m_topup_create = f"{t.m_topup_create_1}{sum_topup}₽* на QIWI кошелек *+79...* с комментарием *№" \
                             f"{get_comm}*{t.m_topup_create_2}"
        elif way_topup == "bank":
            m_topup_create = f"{t.m_topup_create_1}{sum_topup}₽* на карту *1234...* с комментарием *№" \
                            f"{get_comm}*{t.m_topup_create_2}"
        await bot.edit_message_text(m_topup_create, call.from_user.id, call.message.message_id,
                                    reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(
                                        '\U00002705 Перевод выполнил',
                                        callback_data=f"check_topup_{way_topup}_{format(get_comm, '7')}")), parse_mode="Markdown")


#Ручной ввод суммы пополнения или вывода. После выбора ручного ввода. Запрос типа "способ(04)_операция(05)_other_sum" qiwi_topup_other_sum
@dp.callback_query_handler(lambda call: call.data[10:20] == "_other_sum" or call.data[4:20] == "_bet_other_sum")
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
        await FSM.other_sum.set()


#Удаления сообщения. Запрос типа "delete_msg"
@dp.callback_query_handler(lambda call: call.data[:11] == "delete_msg")
async def deleter(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await bot.delete_message(call.message.chat.id, call.message.message_id)


#Проверка пополнения. Запрос типа "(re)check_topup_способ(04)_айди платежа(07)"
@dp.callback_query_handler(lambda call: call.data[:12] == "check_topup_" or call.data[:14] == "recheck_topup_")
async def check_topup(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if call.data[:12] == "check_topup_": N=0
        elif call.data[:14] == "recheck_topup_": N=2
        await b().ButtonTopupCheck(call.from_user.id, call.data[12+N:16+N], call.data[17+N:24+N].lstrip("0"),
                                   call.message.message_id)


#Создание заявки на вывод после подтверждения правильности данных. Запрос типа "confirm_with_способ(04)_сумма(06)_реквизиты(17)"
@dp.callback_query_handler(lambda call: call.data[:13] == "confirm_with_")
async def create_withd(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        sum = call.data[18:24].lstrip("0")
        requisites = call.data[25:42].lstrip("0")
        await db.with_create(call.from_user.id, sum, call.data[13:17], requisites)
        await db.withdraw_balance(call.from_user.id, sum)
        m_with_create = f"\U0000267B *Ваша заявка №{await db.get_with(call.from_user.id, sum, call.data[13:17])} на сумму {sum}₽ успешно зарегистрирована*" \
                        f"\n*Указанные реквизиты - {requisites}*" \
                        f"\n\nВыполнение заявки может занимать до 24 часов"
        await bot.edit_message_text(m_with_create, call.from_user.id, call.message.message_id,
                                    reply_markup=types.InlineKeyboardMarkup().add(await b().button_lk()),
                                    parse_mode="Markdown")


#Проерка ставки и игры. Запрос типа "bet_игра(04)_сумма(06)"
@dp.callback_query_handler(lambda call: call.data[:4] == "bet_")
async def check_bet(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await b().ButtonBetCheck(call)


#Изменение игры. Запрос типа "change_bet"
@dp.callback_query_handler(lambda call: call.data[:11] == "change_bet")
async def changer_bet(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await bot.send_message(call.from_user.id, t.m_type_game,
                              reply_markup=await b().KB_MainGames(), parse_mode="Markdown")


#Создание игровой комнаты и обработка игры. Запрос типа "create_bet_игра(04)_сумма(06)
@dp.callback_query_handler(lambda call: call.data[:11] == "create_bet_")
async def creating_room(call):
    if await ch().rules_checker(call.from_user.id) == (True, False):
        if call.data[11:15] in ("king", "russ", "duel"):
            await b().GameOnline(call.from_user.id, call.data[11:15], call.data[16:22].lstrip("0"), call.message.message_id)
        elif call.data[11:15] in ("bowl", "cube", "slot"):
            await b().GameOffline(call.from_user.id, call.data[11:15], call.data[16:22].lstrip("0"), call.message.message_id)


#История игр
@dp.callback_query_handler(lambda call: call.data[:14] == "story_games_0_")
async def story_games(call):
    await bot.send_message(call.from_user.id, "*Раздел в разработке*",
                           reply_markup=types.InlineKeyboardMarkup().add(await b().button_close()), parse_mode="Markdown")


#Обработчик ручного ввода реквизитов вывода.
@dp.message_handler(content_types=types.ContentType.all(), state=FSM.requisites)
async def user_get_requisites(message: types.Message, state: FSMContext):
    way = (await state.get_data())['way_withd']
    sum = (await state.get_data())['sum_with']
    keyboard = types.InlineKeyboardMarkup()
    try:
        if ((way == "qiwi") and ((len(str(message.text)) != 11) or (message.text[:1] != "7"))) or (way == "bank") and (len(message.text) != 16):
            if (way == "qiwi") and (len(str(message.text)) != 11):
                txt_wrong = "*Неверная длина номера телефона.*\n\nНажмите на кнопку ниже и введите номер телефона еще раз"
            elif (way == "qiwi") and (message.text[:1] != "7"):
                txt_wrong = "*Неверный номер телефона. Номер должен начинаться с 7.*\n\nНажмите на кнопку ниже и введите номер телефона еще раз"
            elif (way == "bank") and (len(message.text) != 16):
                txt_wrong = "*Неверная длина номера карты.*\n\nНажмите на кнопку ниже и введите номер карты еще раз"
            keyboard.add(types.InlineKeyboardButton('\U0000267B Ввести заново',
                                                    callback_data=f"{way}_withd_sum_{format(sum, '06')}"),
                         await b().button_lk())
            await bot.send_message(message.from_user.id, txt_wrong, reply_markup=keyboard, parse_mode="Markdown")
        else:
            if way == "qiwi":
                lineway = "QIWI"
                req = "Номер телефона - *+"
            elif way == "bank":
                lineway = "Карта"
                req = "Номер карты - *"
            keyboard.add(types.InlineKeyboardButton('\U00002705 Подтвердить',
                                                    callback_data=f"confirm_with_{way}_{format(sum, '06')}_{format(message.text, '17')}"),
                         types.InlineKeyboardButton('\U0000267B Изменить', callback_data='withd_balance_main_'))
            await bot.send_message(message.from_user.id, "*Подтвердите правильность данных*"
                                                         f"\n\nСумма - *{sum}₽*"
                                                         f"\nСпособ - *{lineway}*\n{req}{message.text}*",
                                   reply_markup=keyboard, parse_mode="Markdown")
    except:
        keyboard.add(types.InlineKeyboardButton('\U0000267B Ввести заново',
                                                        callback_data=f"{way}_withd_sum_{format(sum, '06')}"),
                     await b().button_lk())
        await bot.send_message(message.from_user.id, "*Неверный формат реквизитов. *"
                                                     "\n\nВыберите одно из действий",
                               reply_markup=keyboard, parse_mode="Markdown")
    await state.finish()


@dp.message_handler(content_types=types.ContentType.STICKER)
async def sticker_reply(message):
    await bot.send_message(message.from_user.id, f"<b>Спасибо за стикер\U0001F928\n"
                                                 f"Информация о стикере</b>\n\n"
                                           f"<b>ID</b>\n<code>{message.sticker.file_id}</code>\n\n"
                                           f"<b>Эмодзи</b>\n<code>{message.sticker.emoji}</code>\n\n"
                                           f"<b>Анимация</b>\n{message.sticker.is_animated}\n\n"
                                                 f"<b>Но все же, давайте лучше сыграем!\U0001F3B0</b>",
                           reply_markup=await b().KeyboardMenu(), parse_mode="HTML")


@dp.message_handler(content_types=types.ContentType.DICE)
async def sticker_reply(message):
    await bot.send_message(message.from_user.id, f"<b>У нас со своим нельзя\U0001F928\n"
                                                 f"Проверьте свою удачу у нас!</b>",
                           reply_markup=await b().KeyboardMenu(), parse_mode="HTML")


#Обработчик ручного ввода суммы пополнения/вывода и ставки
@dp.message_handler(content_types=types.ContentType.all(), state=FSM.other_sum)
async def user_other_sum_enter(message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    if (await state.get_data())['type'] == "oper":
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
        b_enter_again = types.InlineKeyboardButton('\U0000267B Ввести заново',
                                                   callback_data=f"{way}_{oper}_other_sum")
    elif (await state.get_data())['type'] == "bet":
        game = (await state.get_data())['game']
        lineoper = "ставки"
        max_sum = conf.max_bet
        min_sum = conf.min_bet
        if game == "bowl":
            lineway = "Боулинг \U0001F3B3"
        elif game == "cube":
            lineway = "Кубик \U0001F3B2"
        elif game == "slot":
            lineway = "Рулетка \U0001F3B0"
        b_enter_again = types.InlineKeyboardButton('\U0000267B Ввести заново',
                                                   callback_data=f"{game}_bet_other_sum")
    try:
        if (int(message.text) > max_sum) or (int(message.text) < min_sum):
            keyboard.add(b_enter_again, await b().button_lk())
            if int(message.text) > max_sum:
                await bot.send_message(message.from_user.id, f"*Максимальная сумма {lineoper} - {max_sum}₽*"
                                                                "\n\nВыберите одно из действий",
                                   reply_markup=keyboard, parse_mode="Markdown")
            elif int(message.text) < min_sum:
                await bot.send_message(message.from_user.id, f"*Минимальная сумма {lineoper} - {min_sum}₽*"
                                                                  "\n\nВыберите одно из действий",
                                       reply_markup=keyboard, parse_mode="Markdown")
        else:
            if (await state.get_data())['type'] == "oper":
                keyboard.add(types.InlineKeyboardButton('\U00002705 Подтвердить',
                                                        callback_data=f"{way}_{oper}_sum_{format(int(message.text), '06')})"),
                             types.InlineKeyboardButton('\U0000267B Изменить',
                                                        callback_data=f"{oper}_balance_main_"))
                await bot.send_message(message.from_user.id, f"*Подтвердите правильность способа и суммы*"
                                                             f"\n\nСумма {lineoper} - *{int(message.text)}₽*"
                                                             f"\nСпособ {lineoper} - *{lineway}*", reply_markup=keyboard, parse_mode="Markdown")
            elif (await state.get_data())['type'] == "bet":
                await b().ButtonBetCheck(0, message.from_user.id, game, int(message.text))
    except:
        keyboard.add(b_enter_again, await b().button_lk())
        await bot.send_message(message.from_user.id, "*Неверный формат числа. *"
                                                          "\n\nВыберите одно из действий",
                                   reply_markup=keyboard, parse_mode="Markdown")
    await state.finish()


# Админский обработчик запроса подтверждения и подтверждения транзакции. Запрос типа (adm)(chk)_accure_тип транзакции(05)_
# айди транзакции
@dp.callback_query_handler(lambda call: call.data[:11] in ("adm_accure_", "chk_accure_"))
async def change_trans_type(call):
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
                await bot.edit_message_text(f"*Транзакция №{trans_id} успешно подтверждена!*",
                                                  adm_id, call.message.message_id,
                                            reply_markup=types.InlineKeyboardMarkup(1).add(
                                                types.InlineKeyboardButton('\U0000267B Другая транзакция',
                                                                   callback_data="control_transact"),
                                                await b().button_adm_lk()), parse_mode="Markdown")
            elif call.data[:3] == "chk":
                if trans_type == "topup":
                    way = "пополнения"
                elif trans_type == "withd":
                    way = "вывода"
                await bot.edit_message_text(f"*Вы хотите подтвердить транзакцию {way} №{trans_id}?*",
                                                  call.from_user.id, call.message.message_id,
                                            reply_markup=types.InlineKeyboardMarkup(1).add(
                                                types.InlineKeyboardButton('\U00002705 Да',
                                                        callback_data=f"adm_accure_{trans_type}_{trans_id}"),
                                                await b().button_adm_lk()), parse_mode="Markdown")
        else:
            await b().not_ehough_access(adm_id, "1 (Middle)", call.message.message_id)
    else:
        await b().bpmanag_no_valid(adm_id, True, call.message.message_id)


#Админский обработчик с выбором типа желаемой транзакции
@dp.callback_query_handler(lambda call: call.data == "control_transact")
async def choose_trans_type(call):
    if await db.adm_valid_check(call.from_user.id):
        await bot.edit_message_text(t.m_adm_type_trans, call.from_user.id, call.message.message_id,
                                    parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup(2).add(
                types.InlineKeyboardButton('Пополнение', callback_data=f"accure_topup"),
                types.InlineKeyboardButton('Вывод', callback_data=f"accure_withd"),
                await b().button_adm_lk("\U00002B05")))
    else:
        await b().bpmanag_no_valid(call.from_user.id, True, call.message.message_id)


@dp.callback_query_handler(lambda call: call.data == "control_users")
async def enter_user(call, state: FSMContext):
    if await db.adm_valid_check(call.from_user.id):
        await bot.edit_message_text("*Введите ник или айди пользователя*", call.from_user.id, call.message.message_id, parse_mode="Markdown")
        await state.update_data(id_adm=call.from_user.id)
        await FSM.enter_id_user.set()
    else:
        await b().bpmanag_no_valid(call.from_user.id, True, call.message.message_id)


@dp.message_handler(content_types=types.ContentType.all(), state=FSM.enter_id_user)
async def get_id_trans(message: types.Message, state: FSMContext):
    adm_id = (await state.get_data())['id_adm']
    if message.text.isdigit() and await db.user_exists(message.text) or await db.user_exists(message.text, "username"):
        await bot.send_message(adm_id, "*Пользователь найден*",
                               reply_markup=types.InlineKeyboardMarkup(1).add(
                                   types.InlineKeyboardButton("\U0000267B Ввести заново",
                                                              callback_data="control_users"),
                                   await b().button_adm_lk()),
                               parse_mode="Markdown")
    else:
        await bot.send_message(adm_id, "*Данный пользователь не найден*", reply_markup=types.InlineKeyboardMarkup(1).add(
            types.InlineKeyboardButton("\U0000267B Ввести заново", callback_data="control_users"), await b().button_adm_lk()),
                               parse_mode="Markdown")
    await state.finish()

# Админский обработчик ручного ввода номера транзакции. Запрос типа accure_тип транзакции(05)
@dp.callback_query_handler(lambda call: call.data[:7] == "accure_")
async def accure_trans(call, state: FSMContext):
    if await db.adm_valid_check(call.from_user.id):
        if call.data[7:12] == "topup":
            await bot.edit_message_text(t.m_enter_num_topup, call.from_user.id, call.message.message_id, parse_mode="Markdown")
        elif call.data[7:12] == "withd":
            await bot.edit_message_text(t.m_enter_num_withd, call.from_user.id, call.message.message_id, parse_mode="Markdown")
        await state.update_data(id_adm=call.from_user.id, trans_type=call.data[7:12])
        await FSM.accure_id_trans.set()
    else:
        await b().bpmanag_no_valid(call.from_user.id, True, call.message.message_id)


#Админский обработчик подтверждения смены способа вывода. Запрос типа chk_withd_change_way_айди вывода
@dp.callback_query_handler(lambda call: call.data[:21] == "chk_withd_change_way_")
async def change_withd_way(call):
    if await db.adm_valid_check(call.from_user.id):
        if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
            if await db.get_withd_way(call.data[21:]) == "bank":
                button_another_way = types.InlineKeyboardButton("QIWI", callback_data=f"rqs_withd_change_qiwi_{call.data[21:]}")
                way_withd_write = "Банковская карта"
            elif await db.get_withd_way(call.data[21:]) == "qiwi":
                button_another_way = types.InlineKeyboardButton("Банковская карта", callback_data=f"rqs_withd_change_bank_{call.data[21:]}")
                way_withd_write = "QIWI"
            await bot.edit_message_text(f"*Текущий способ вывода транзакции №{call.data[21:]} - {way_withd_write}"
                                                   "\n\nВозможность изменить способ вывода на:*", call.from_user.id,
                                              call.message.message_id, reply_markup=types.InlineKeyboardMarkup(1).add(
                    button_another_way, await b().button_adm_lk()), parse_mode="Markdown")
        else:
            await b().not_ehough_access(call.from_user.id, "2 (Master)", call.message.message_id)
    else:
        await b().bpmanag_no_valid(call.from_user.id, True, call.message.message_id)


# Админский обработчик ручного ввода новых реквизитов. Запрос типа rqs_withd_change_способ вывода(04)_старый способ(04)
@dp.callback_query_handler(lambda call: call.data[:17] == "rqs_withd_change_")
async def get_new_req(call, state: FSMContext):
    if await db.adm_valid_check(call.from_user.id):
        if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
            await bot.edit_message_text(t.m_enter_new_requisites, call.from_user.id, call.message.message_id,
                                              parse_mode="Markdown")
            await state.update_data(id_adm=call.from_user.id, new_way=call.data[17:21],
                                    old_way=await db.get_withd_way(call.data[22:]), with_id=call.data[22:])
            await FSM.adm_new_requis.set()
        else:
            await b().not_ehough_access(call.from_user.id, "2 (Master)", call.message.message_id)
    else:
        await b().bpmanag_no_valid(call.from_user.id, True, call.message.message_id)


#Админская панель отображения измененных данных вывода
@dp.message_handler(content_types=types.ContentType.all(), state=FSM.adm_new_requis)
async def get_id_trans(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup(1)
    adm_id = data['id_adm']
    with_id = int(data['with_id'])
    if await db.adm_valid_check(adm_id):
        if await db.adm_lvl_check(adm_id) > conf.middle_lvl:
            try:
                new_req = int(message.text)
                if data['new_way'] == "bank":
                    if len(new_req) != 16:
                        raise
                    new_way_w = "Банковская карта"
                elif data['new_way'] == "qiwi":
                    if len(new_req) != 11 or new_req[0] != "7":
                        raise
                    new_way_w = "QIWI"
                if data['new_way'] != data['old_way']:
                    about_new_way = f"Новый способ - {new_way_w}\n"
                else:
                    about_new_way = ""
                keyboard.add(types.InlineKeyboardButton("\U00002705 Подтвердить",
                                                        callback_data=f"adm_withd_change_{data['new_way']}_{format(with_id, '010')}_{new_req}"),
                             await b().button_adm_lk())
                await bot.send_message(adm_id, f"*Желаемые изменения: \n\nТранзакция №{with_id}\n"
                                               f"{about_new_way}Новые реквизиты - {new_req}*", reply_markup=keyboard,
                                       parse_mode="Markdown")
            except:
                keyboard.add(types.InlineKeyboardButton("\U0000267B Ввести заново",
                                                        callback_data=f"rqs_withd_change_{data['new_way']}_{with_id}"),
                             await b().button_adm_lk())
                await bot.send_message(adm_id, "*Неверные реквизиты\n\nВыберите одно из действий:*", reply_markup=keyboard, parse_mode="Markdown")
        else:
            await b().not_ehough_access(adm_id, "2 (Master)")
    else:
        await b().bpmanag_no_valid(adm_id, False)
    await state.finish()


# Админский обработчик изменения транзакции вывода. Запрос типа adm_withd_change_способ(04)_
# айди транзакции(10)_новые реквизиты
@dp.callback_query_handler(lambda call: call.data[:17] == "adm_withd_change_")
async def change_withd_way(call):
    if await db.adm_valid_check(call.from_user.id):
        if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
            await db.update_withd(call.data[22:32].lstrip("0"), call.data[17:21], call.data[33:])
            if call.data[17:21] == "bank":
                new_way_w = "Банковская карта"
            else:
                new_way_w = "QIWI"
            await bot.edit_message_text(f"*Текущая информация: \n\nТранзакция №{call.data[22:32].lstrip('0')}\nСпособ - {new_way_w}"
                                              f"\nРеквизиты - {call.data[33:]}*", call.from_user.id,
                                              call.message.message_id, reply_markup=types.InlineKeyboardMarkup(1).add(
                    types.InlineKeyboardButton('\U0000267B Другая транзакция',
                                               callback_data="control_transact"),
                    await b().button_adm_lk()), parse_mode="Markdown")
        else:
            await b().not_ehough_access(call.from_user.id, "2 (Master)", call.message.message_id)
    else:
        await b().bpmanag_no_valid(call.from_user.id, False)


#Админская панель отображения транзакций
@dp.message_handler(content_types=types.ContentType.all(), state=FSM.accure_id_trans)
async def get_id_trans(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keyboard = types.InlineKeyboardMarkup(1)
    id_adm = data['id_adm']
    trans_type = data['trans_type']
    b_adm_trans = types.InlineKeyboardButton('\U0000267B Другая транзакция',
                                             callback_data="control_transact")
    try:
        int(message.text)
        if await db.adm_valid_check(id_adm):
            if 0 < int(message.text) < 100000:
                if trans_type == "topup":
                    id_get_trans, user, way, sum, time_cr, accure, done, time_do, oper = [str(x) for x in await db.adm_info_topup(message.text)]
                    if accure == "False":
                        accure_w = "\U0000274C"
                    else:
                        accure_w = "\U00002705"
                elif trans_type == "withd":
                    id_get_trans, user, way, sum, time_cr, done, time_do, oper, requisites = [str(x) for x in await db.adm_info_withd(message.text)]
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
                username    = str(await db.find_username(user))
                if username == "None":
                    username = "Никнейм отсуствует"
                else:
                    username = f"@{username}"
                if trans_type == "topup":
                    if accure == "False" and await db.adm_lvl_check(id_adm) > conf.junior_lvl:
                        keyboard.add(types.InlineKeyboardButton('\U00002705 Подтвердить транзакцию',
                                                               callback_data=f"chk_accure_topup_{id_get_trans}"))
                    keyboard.add(b_adm_trans, await b().button_adm_lk())
                    await bot.send_message(id_adm, f"Транзакция №{id_get_trans}"
                                                   f"\nПользователь - {username} (id<code>{user}</code>)"
                                                   f"\nСпособ - {way_w}"
                                                   f"\nСумма - {sum} ₽"
                                                   f"\nВремя создания - {time_cr}"
                                                   f"\nПеревод выполнен - {accure_w}"
                                                   f"\nПополнение завершено - {done_w}"
                                                   f"\nВремя завершения - {time_do_w}",
                                           reply_markup=keyboard, parse_mode="HTML")
                elif trans_type == "withd":
                    if done == "False" and await db.adm_lvl_check(id_adm) > conf.junior_lvl:
                        keyboard.add(types.InlineKeyboardButton('\U00002705 Подтвердить транзакцию',
                                                                   callback_data=f"chk_accure_withd_{id_get_trans}"))
                        if await db.adm_lvl_check(id_adm) > conf.middle_lvl:
                            keyboard.add(types.InlineKeyboardButton('\U0000267B Изменить способ',
                                                                       callback_data=f"chk_withd_change_way_{id_get_trans}"),
                                         types.InlineKeyboardButton('\U0000267B Изменить реквизиты',
                                                                       callback_data=f"rqs_withd_change_{way}_{id_get_trans}"))
                    keyboard.add(b_adm_trans, await b().button_adm_lk())
                    await bot.send_message(id_adm, f"Транзакция №{id_get_trans}"
                                                   f"\nПользователь - {username} (id<code>{user}</code>)"
                                                   f"\nСпособ - {way_w}"
                                                   f"\nСумма - {sum} ₽"
                                                   f"\nВремя создания - {time_cr}"
                                                   f"\nВывод завершен - {done_w}"
                                                   f"\nВремя завершения - {time_do_w}"
                                                   f"\nРеквизиты - <code>{requisites}</code>",
                                           reply_markup=keyboard, parse_mode="HTML")
            else:
                raise
        else:
            await b().bpmanag_no_valid(id_adm, False)
    except:
        keyboard.add(b_adm_trans, await b().button_adm_lk())
        await bot.send_message(message.from_user.id, f"*Транзакция с таким номером не найдена.*"
                                                          "\n\nВыберите одно из действий",
                                   reply_markup=keyboard, parse_mode="Markdown")
    await state.finish()


@dp.message_handler(lambda message: message.text == "\U0001F464 Личный кабинет")
async def account(message):
    await ch().data_checker(message.from_user)
    if await ch().rules_checker(message.from_user.id) == (True, False):
        text, keyboard = await b().ButtonAccount(message.from_user.id)
        await bot.send_message(message.from_user.id, text, reply_markup=keyboard, parse_mode="Markdown")


@dp.message_handler(lambda message: message.text == "\U0001F4AC Поддержка")
async def main_rules(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.delete()
        await bot.send_message(message.from_user.id, t.m_support, reply_markup=types.InlineKeyboardMarkup(1).add(
            await b().button_support(), await b().button_close()), parse_mode="Markdown")


@dp.message_handler(lambda message: message.text == "\U0001F4D5 Правила")
async def main_new_rules(message):
    await message.delete()
    await bot.send_message(message.from_user.id, t.m_rules, parse_mode="Markdown")


@dp.message_handler(lambda message: message.text == "\U00002705 Принять правила")
async def main_start(message):
    await bot.send_message(message.from_user.id, t.m_start_new, reply_markup=await b().KB_Start())
    await db.rules_accept(message.from_user.id)


@dp.message_handler(lambda message: message.text in ("\U00002139 Меню", "\U00002B05 В меню", "\U0001F680 Начать пользование"))
async def main(message: types.Message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await bot.send_message(message.from_user.id, t.m_you_in_menu,
                               reply_markup=await b().KB_Menu(), parse_mode="Markdown")


@dp.message_handler(lambda message: message.text in ("\U0001F3AE Игры", "\U00002B05 К играм", "\U00002B05 Назад"))
async def main_games(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await bot.send_message(message.from_user.id, t.m_type_game,
                               reply_markup=await b().KB_MainGames(), parse_mode="Markdown")


@dp.message_handler(lambda message: message.text in ("\U0001F4BB Онлайн"))
async def main_games(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await bot.send_message(message.from_user.id, t.m_games_choose,
                               reply_markup=await b().KB_OnlineGames(), parse_mode="Markdown")


@dp.message_handler(lambda message: message.text in ("\U0001F680 Быстрая игра"))
async def main_games(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await bot.send_message(message.from_user.id, t.m_games_choose,
                               reply_markup=await b().KB_OfflineGames(), parse_mode="Markdown")


@dp.message_handler(lambda message: message.text == "\U00002139 Справка")
async def info_bot(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await bot.send_message(message.from_user.id, t.m_main_info,
                               reply_markup=await b().KB_Info(), parse_mode="Markdown")


@dp.message_handler(lambda message: message.text in ("\U0001F4AC Комиссия", "\U0001F4AC Алгоритмы", "\U0001F4AC Правила"))
async def que_answ(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        await message.delete()
        await bot.send_message(message.from_user.id, t.dct_que_answ[message.text],
                               reply_markup=types.InlineKeyboardMarkup().add(
                                   await b().button_close()), parse_mode="Markdown")


@dp.message_handler(lambda message: message.text in ("\U0001F93A Дуэль", "\U0001F3B2 Русская рулетка",
                                                     "\U0001F451 Королевская битва", "\U0001F3B3 Боулинг",
                                                     "\U0001F3B2 Бросить кубик", "\U0001F3B0 Крутить рулетку"))
async def online_game_bet(message):
    if await ch().rules_checker(message.from_user.id) == (True, False):
        text, keyboard = await b().KBT_GameBet(message.text)
        await bot.send_message(message.from_user.id, text, reply_markup=keyboard, parse_mode="Markdown")

executor.start_polling(dp)