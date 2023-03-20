import random

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from configs import conf

from filters.is_forwarded import ForwardedFilter
from callback_factory import BalanceManageCallback, AdminManageCallback
from middlewares.ban_rules_check import BanRulesMsgMiddleware
from middlewares.bot_blocked_check import BotBlockedMsgMiddleware
from db_conn_create import db
from configs.logs_config import logs

from fsm import FSM
from templates.texts import TextsTg as t
from templates.buttons import ButtonsTg as b
from checkers import Checkers as ch
from templates.messages import Messages as msg

router = Router()
router.message.middleware(BanRulesMsgMiddleware())
router.message.outer_middleware(BotBlockedMsgMiddleware())


@router.message(ForwardedFilter())
async def uni_reply(message):
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
                [types.InlineKeyboardButton(text="\U0001F4D6 Информация о пользователе",
                                           callback_data=AdminManageCallback(action="user_info", user_id=message.forward_from.id).pack())]
            ])
        else:
            keyboard = await b().KB_Menu()
        await message.answer(f"<b>Пересланное сообщение от {text_user}</b>\n\n"
                             f"<b>ID {text_user} - </b><code>{message.forward_from.id}</code>\n"
                             f"<b>Имя {text_user} - </b>{message.forward_from.first_name}\n"
                             f"<b>Никнейм - </b><code>{nickname}</code>",
                             reply_markup=keyboard)
    elif message.forward_from_chat:
        await message.answer(f"<b>Пересланное сообщение из канала</b>\n\n"
                             f"<b>ID чата - </b><code>{message.forward_from_chat.id}</code>\n"
                             f"<b>Название чата - </b>{message.forward_from_chat.title}",
                             reply_markup=await b().KB_Menu())
    elif message.forward_sender_name:
        await message.answer(
            f"<b>Пользователь запретил доступ к собственной информации настройками приватности</b>",
            reply_markup=await b().KB_Menu())


@router.callback_query(BalanceManageCallback.filter(F.action == "choose_way"))
async def way_tw(call: types.CallbackQuery, callback_data: BalanceManageCallback):
    if callback_data.from_where == "main":
        b_back = await b().BT_Lk("\U00002B05")
    else:
        b_back = types.InlineKeyboardButton(text='\U00002B05 Назад', callback_data=BalanceManageCallback(action="choose_bet", from_where=callback_data.from_where).pack())
    buttons = [
        [
            types.InlineKeyboardButton(text='\U0001F95D QIWI',
                                       callback_data=BalanceManageCallback(operation=callback_data.operation, way="qiwi", action="choose_sum", from_where=callback_data.from_where).pack()),
            types.InlineKeyboardButton(text='\U0001F4B3 Карта',
                                       callback_data=BalanceManageCallback(operation=callback_data.operation, way="bank", action="choose_sum", from_where=callback_data.from_where).pack())
        ],
        [b_back]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.edit_text(text=t.dct_type_way[callback_data.operation], reply_markup=keyboard)
    await call.answer()


@router.callback_query(lambda call: call.data == "back_to_acc")
async def back_acc(call):
    await ch().data_checker(call.from_user)
    text, keyboard = await b().KBT_Account(call.from_user.id)
    await call.message.edit_text(text=text, reply_markup=keyboard)
    await call.answer()


@router.callback_query(BalanceManageCallback.filter(F.action == "enter_requisites"))
async def enter_req(call: types.CallbackQuery, callback_data: BalanceManageCallback, state: FSMContext):
    if callback_data.sum <= await db.get_user_balance(call.from_user.id):
        await call.message.edit_text(text=t.dct_enter_req[callback_data.way])
        await state.update_data(way_withd=callback_data.way, sum_with=callback_data.sum)
        await state.set_state(FSM.requisites)
    elif callback_data.sum > await db.get_user_balance(call.from_user.id):
        m_no_money = f"\U0000274C <b>Недостаточно средств на балансе для вывода {callback_data.sum}₽" \
                     f"\n\nВаш баланс: {await db.get_user_balance(call.from_user.id)}₽</b>\n\nПопробуйте выбрать другую сумму"
        await call.message.edit_text(text=m_no_money, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[await b().BT_Lk()]))
        await call.answer()


@router.callback_query(lambda call: call.data[:4] == "que_")
async def info_games(call: types.CallbackQuery):
    await call.message.edit_text(t.dct_games_que[call.data[4:8]], reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                    [types.InlineKeyboardButton(text='\U00002B05 Назад',
                                                               callback_data=BalanceManageCallback(action="choose_bet", from_where=call.data[4:8]).pack())]
                                ]))
    await call.answer()


@router.callback_query(BalanceManageCallback.filter(F.action == "choose_bet"))
async def back_games(call: types.CallbackQuery, callback_data: BalanceManageCallback):
    text, keyboard = await b().KBT_GameBet(callback_data.from_where)
    await call.message.edit_text(text=text, reply_markup=keyboard)
    await call.answer()


@router.callback_query(lambda call: call.data[:12] in ("story_topup_", "story_toadm_", "story_games_", "story_gaadm_"))
async def story_oper(call):
    if call.data[6:11] in ("toadm", "gaadm"):
        if await db.adm_valid_check(call.from_user.id):
            user_id = call.data[20:]
            if call.data[6:11] == "toadm":
                adm_line = f"<b>Операции пользователя - <code>{user_id}</code></b>\n\n"
            else:
                adm_line = f"<b>Игры пользователя - <code>{user_id}</code></b>\n\n"
        else:
            logs.warning(
                f"Not valid admin {call.from_user.id} tried to get access to admin panel with call - {call}")
            return await msg().adm_no_valid(call, "call")
    else:
        adm_line = ""
        user_id = call.from_user.id
    N = conf.base_num
    if call.data[6:11] in ("topup", "toadm"):
        count_lines = await db.get_topup_lines(user_id) + await db.get_withd_lines(user_id)
    else:
        count_lines = await db.get_games_lines(user_id)
    buttons = []
    if count_lines == 0:
        buttons.append(await b().BT_Close())
        if call.data[6:11] in ("topup", "toadm"):
            if call.data[6:11] == "toadm":
                await call.message.answer("<b>У пользователя нет операций</b>",
                                          reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[buttons]))
            else:
                await call.message.answer("<b>У вас пока что нет операций</b>",
                                          reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[buttons]))
        else:
            if call.data[6:11] == "gaadm":
                await call.message.answer("<b>У пользователя нет игр</b>",
                                          reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[buttons]))
            else:
                await call.message.answer("<b>У вас пока что нет игр</b>",
                                          reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[buttons]))
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
            if N == 0:
                N = conf.base_num
        dateold = None
        if call.data[6:11] in ("topup", "toadm"):
            story_topup = f"<b>{adm_line}Всего операций - {count_lines}\nОперации с {(current_page - 1) * conf.base_num + 1} по {(current_page - 1) * conf.base_num + N}:</b>\n"
        else:
            story_topup = f"<b>{adm_line}Всего игр - {count_lines}\nИгры с {(current_page - 1) * conf.base_num + 1} по {(current_page - 1) * conf.base_num + N}:</b>\n"
        while N != 0:
            if count_lines < conf.base_num or current_page == max_page:
                num_from = count_lines - N + 1
            elif current_page != max_page:
                num_from = current_page * conf.base_num - N + 1
            if call.data[6:11] in ("topup", "toadm"):
                comm, way, sum, done, oper, time_cr = [str(x) for x in await db.get_story_oper(user_id, num_from)]
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
            else:
                user_num, warned, win_sum, bal_before, id_room, win_num, is_full, is_end, time_cr, time_end, bet, game = [str(x) for x in await db.get_story_game(user_id, num_from)]
                gamename = {
                    "duel": "\U0001F93A Дуэль",
                    "king": "\U0001F3B2 Королевская битва",
                    "russ": "\U0001F451 Русская рулетка",
                    "bowl": "\U0001F3B3 Боулинг",
                    "cube": "\U0001F3B2 Кубик",
                    "slot": "\U0001F3B0 Рулетка"
                }[game]
                if is_full == "True":
                    is_full_line = "\U00002705"
                else:
                    is_full_line = "\U0000274C"
                if is_end == "True":
                    is_end_line = "\U00002705"
                else:
                    is_end_line = "\U0000274C"
                if warned == "True":
                    is_warned_line = "\U00002705"
                else:
                    is_warned_line = "\U0000274C"
                if win_sum == "None":
                    win_sum_line = ""
                else:
                    if float(win_sum) > 0:
                        win_sum_line = f"<b>Выигрыш  - {int(float(win_sum))}₽ \U0001F4C8</b>\n" \
                                       f"Баланс <b>до/после</b> игры - <b>{int((float(bal_before)))}/{int(float(bal_before)-float(bet)+float(win_sum))}₽</b>\n"
                    else:
                        win_sum_line = f"<b>Поражение \U0001F4C9</b>\n" \
                                       f"Баланс <b>до/после</b> игры - <b>{int(float(bal_before))}/{int(float(bal_before)-float(bet))}₽</b>\n"
                if game in ("duel", "russ", "king"):
                    if win_num == "0":
                        win_num_line = "<b>Игра еще не завершена</b>"
                    else:
                        win_num_line = f"Выпавшее число - <b>{win_num}</b>"
                    if call.data[6:11] == "games":
                        game_result_num = f"Ваше число - <b>{user_num}</b>\n{win_num_line}"
                    else:
                        game_result_num = f"Число пользователя - <b>{user_num}</b>\n{win_num_line}"
                else:
                    game_result_num = f"Выпавшая комбинация - <b>{win_num}</b>"
                if call.data[6:11] == "gaadm":
                    adm_game_result = f"Комната заполнена - <b>{is_full_line}</b>\n" \
                                      f"Игра завершена - <b>{is_end_line}</b>\n" \
                                      f"Пользователь уведомлен - <b>{is_warned_line}</b>\n" \
                                      f"Время создания - <b>{time_cr[:19]}</b>\n" \
                                      f"Время завершения - <b>{time_end[:19]}</b>\n"
                else:
                    adm_game_result = ""
                all_line = f"<b>{gamename} №{id_room}</b>\nСтавка - <b>{bet}₽</b>\n{game_result_num}\n{win_sum_line}{adm_game_result}"
                if dateold == time_cr[:10]:
                    line = f"<em>-{time_cr[11:16]}</em> - {all_line}\n"
                if dateold != time_cr[:10]:
                    dateline = f"<b>• {time_cr[:10]}</b>\n"
                    line = f"{dateline}<em>-{time_cr[11:16]}</em> - {all_line}\n"
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
        if call.data[6:11] in ("toadm", "gaadm"):
            buttons.append(
                [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                            callback_data=AdminManageCallback(action="user_info", user_id=user_id).pack())])
            buttons.append([await b().BT_AdmLk()])
        else:
            buttons.append([await b().BT_Lk()])
        await call.answer()
        await call.message.edit_text(text=story_topup,
                                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
        await call.answer()


@router.callback_query(BalanceManageCallback.filter(F.action == "choose_sum"))
async def choose_sum_topup(call: types.CallbackQuery, callback_data: BalanceManageCallback):
    if callback_data.way == "qiwi":
        emoji = "\U0001F95D"
    elif callback_data.way == "bank":
        emoji = "\U0001F4B3"
    await call.message.edit_text(text=f"{emoji} <b>Выберите желаемую сумму:</b>", reply_markup=await b().KB_Sum(
                                    "oper", callback_data.operation, callback_data.way, callback_data.from_where))
    await call.answer()


@router.callback_query(BalanceManageCallback.filter(F.action == "create_request"), BalanceManageCallback.filter(F.operation == "topup"))
async def info_topup(call: types.CallbackQuery, callback_data: BalanceManageCallback):
    with open(f'difs/{callback_data.way[:1]}wallets.txt', 'r') as wallet:
        with open(f'difs/{callback_data.way[:1]}wallets.txt', 'r') as counter:
            max = sum(1 for line in counter) - 1
            counter.close()
        req = (wallet.readlines())[random.randint(0, max)]
        wallet.close()
    await db.topup_create(call.from_user.id, callback_data.sum, callback_data.way, int(req))
    get_comm = await db.get_comm(call.from_user.id, callback_data.sum, callback_data.way)
    if callback_data.way == "qiwi":
        url_link = "https://qiwi.com/payment/form/99"
        m_topup_create = f"{t.m_topup_create_1}<b>{callback_data.sum}₽</b> на QIWI кошелек <code>+{req}</code> с комментарием <b>№" \
                         f"{get_comm}</b>{t.m_topup_create_2}"
    elif callback_data.way == "bank":
        url_link = "https://yoomoney.ru/transfer/a2c"
        m_topup_create = f"{t.m_topup_create_1}<b>{callback_data.sum}₽</b> на карту <code>{req}</code> с комментарием <b>№" \
                         f"{get_comm}</b>{t.m_topup_create_2}"
    await call.message.edit_text(text=m_topup_create, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                    [types.InlineKeyboardButton(text='\U0001F4B8 Оплатить', url=url_link)],
                                    [types.InlineKeyboardButton(text='\U00002705 Перевод выполнил',
                                                                callback_data=BalanceManageCallback(action="check_topup", id_oper=get_comm, id_msg=call.message.message_id).pack())]]),)
    await call.answer()


@router.callback_query(BalanceManageCallback.filter(F.action == "choose_other"))
async def enter_sum_topup(call: types.CallbackQuery, callback_data: BalanceManageCallback, state: FSMContext):
    if callback_data.operation in ("topup", "withd"):
        if callback_data.operation == "withd":
            await call.message.edit_text(text=f"<b>Введите сумму вывода:</b>\n\nМаксимальная сумма - <b>{conf.max_tw}₽</b>\n"
                                        f"Минимальная сумма - <b>{conf.min_tw}₽</b>\n Сумма должна быть <b>целым</b> числом (без копеек)")
        else:
            await call.message.edit_text(text=f"<b>Введите сумму пополнения:</b>\n\nМаксимальная сумма - <b>{conf.max_tw}₽</b>\n"
                                        f"Минимальная сумма - <b>{conf.min_tw}₽</b>\nСумма должна быть <b>целым</b> числом (без копеек)")
        await state.update_data(type="oper", oper=callback_data.operation, way=callback_data.way)
    else:
        await call.message.edit_text(text=f"Введите желаемую сумму ставки:\n\nМаксимальная сумма - <b>{conf.max_bet}₽</b>"
                                    f"\nМинимальная сумма - <b>{conf.min_bet}₽</b>\nСумма должна быть <b>целым</b> числом (без копеек)")
        await state.update_data(type="bet", game=callback_data.game)
    await call.answer()
    await state.set_state(FSM.other_sum)


@router.callback_query(lambda call: call.data[:11] == "delete_msg")
async def deleter(call):
    await call.message.delete()
    await call.answer()


@router.callback_query(BalanceManageCallback.filter(F.action == "check_topup"))
async def check_topup(call: types.CallbackQuery, callback_data: BalanceManageCallback):
    await ch().topup_checker_user(call.message, callback_data.id_oper)
    await call.answer()


@router.callback_query(BalanceManageCallback.filter(F.action == "create_request"), BalanceManageCallback.filter(F.operation == "withd"))
async def create_withd(call: types.CallbackQuery, callback_data: BalanceManageCallback):
    await db.with_create(call.from_user.id, callback_data.sum, callback_data.way, callback_data.requisites)
    await db.set_withdraw_balance(call.from_user.id, callback_data.sum)
    m_with_create = f"\U0000267B <b>Ваша заявка №{await db.get_with(call.from_user.id, callback_data.sum, callback_data.way)} на сумму {callback_data.sum}₽ успешно зарегистрирована</b>" \
                    f"\n<b>Указанные реквизиты - {callback_data.requisites}</b>" \
                    f"\n\nВыполнение заявки может занимать до 24 часов"
    await call.message.edit_text(text=m_with_create, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[await b().BT_Lk()]]))
    await call.answer()


@router.callback_query(BalanceManageCallback.filter(F.action == "change_bet"))
async def changer_bet(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer("\U0001F914 Выберите тип игры",
                              reply_markup=await b().KB_MainGames())
    await call.answer()


@router.callback_query(BalanceManageCallback.filter(F.action == "check_bet"))
@router.callback_query(BalanceManageCallback.filter(F.action == "create_bet"))
async def creating_room(call: types.CallbackQuery, callback_data: BalanceManageCallback):
    await ch().bet_sum_checker(call.message, callback_data.game, callback_data.sum, callback_data.action, call.message.message_id)
    await call.answer()


@router.message(FSM.requisites)
async def user_get_requisites(message: types.Message, state: FSMContext):
    way = (await state.get_data())['way_withd']
    sum = (await state.get_data())['sum_with']
    try:
        if not message.text.isdigit():
            raise
        if ((way == "qiwi") and ((len(str(message.text)) != 11) or (message.text[:1] != "7"))) or (
                way == "bank") and (len(message.text) != 16):
            if (way == "qiwi") and (len(str(message.text)) != 11):
                txt_wrong = "<b>Неверная длина номера телефона.</b>\n\nНажмите на кнопку ниже и введите номер телефона еще раз"
            elif (way == "qiwi") and (message.text[:1] != "7"):
                txt_wrong = "<b>Неверный номер телефона. Номер должен начинаться с 7.</b>\n\nНажмите на кнопку ниже и введите номер телефона еще раз"
            elif (way == "bank") and (len(message.text) != 16):
                txt_wrong = "<b>Неверная длина номера карты.</b>\n\nНажмите на кнопку ниже и введите номер карты еще раз"
            await message.answer(txt_wrong, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                            callback_data=BalanceManageCallback(action="enter_requisites", operation="withd", way=way, sum=sum).pack())],
                [await b().BT_Lk()]
            ]))
        else:
            if way == "qiwi":
                lineway = "QIWI"
                req = "Номер телефона - <b>+"
            elif way == "bank":
                lineway = "Карта"
                req = "Номер карты - <b>"
            await message.answer("<b>Подтвердите правильность данных</b>"
                                 f"\n\nСумма - <b>{sum}₽</b>"
                                 f"\nСпособ - <b>{lineway}</b>\n{req}{message.text}</b>",
                                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                     [types.InlineKeyboardButton(text='\U00002705 Подтвердить',
                                                                 callback_data=BalanceManageCallback(action="create_request", sum=sum, operation="withd", way=way, requisites=message.text).pack())],
                                     [types.InlineKeyboardButton(text='\U0000267B Изменить',
                                                                 callback_data=BalanceManageCallback(operation="withd", from_where="main", action="choose_way").pack())]
                                 ]))
    except:
        logs.info(f"User {message.from_user.id} tried to enter requisites {message.text}")
        await message.answer("<b>Неверный формат реквизитов.</b>"
                             "\n\nВыберите одно из действий",
                             reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                 [types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                             callback_data=BalanceManageCallback(action="enter_requisites", operation="withd", sum=sum, way=way).pack())],
                                 [await b().BT_Lk()]
                             ]))
    await state.clear()


@router.message(F.sticker)
async def sticker_reply(message):
    await message.answer(f"<b>Спасибо за стикер\U0001F928\n"
                         f"Информация о стикере</b>\n\n"
                         f"<b>ID</b>\n<code>{message.sticker.file_id}</code>\n\n"
                         f"<b>Эмодзи</b>\n<code>{message.sticker.emoji}</code>\n\n"
                         f"<b>Анимация</b>\n{message.sticker.is_animated}\n\n"
                         f"<b>Но все же, давайте лучше сыграем!\U0001F3B0</b>",
                         reply_markup=await b().KB_Menu())


@router.message(F.dice)
async def dice_reply(message):
    await message.answer(f"<b>У нас со своим нельзя\U0001F928\n"
                         f"Проверьте свою удачу у нас!</b>",
                         reply_markup=await b().KB_Menu())


@router.message(FSM.other_sum)
async def user_other_sum_enter(message, state: FSMContext):
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
        b_enter_again = types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                   callback_data=AdminManageCallback(action="user_balance", user_id=user_id, key=way, operation="other").pack())
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
                                                   callback_data=BalanceManageCallback(action="choose_other", operation=oper, way=way).pack())
    elif (await state.get_data())['type'] == "bet":
        game = (await state.get_data())['game']
        lineoper = "ставки"
        max_sum = conf.max_bet
        min_sum = conf.min_bet
        b_enter_again = types.InlineKeyboardButton(text='\U0000267B Ввести заново',
                                                   callback_data=BalanceManageCallback(action="choose_other", operation="bet", game=game).pack())
    try:
        if not message.text.isdigit():
            raise
        if (int(message.text) > max_sum) or (int(message.text) < min_sum):
            buttons.append([b_enter_again])
            if (await state.get_data())['type'] == "admin":
                buttons.append([await b().BT_AdmLk()])
            else:
                buttons.append([await b().BT_Lk()])
            if int(message.text) > max_sum:
                await message.answer(f"<b>Максимальная сумма {lineoper} - {max_sum}₽</b>"
                                     "\n\nВыберите одно из действий",
                                     reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
            elif int(message.text) < min_sum:
                await message.answer(f"<b>Минимальная сумма {lineoper} - {min_sum}₽</b>"
                                     "\n\nВыберите одно из действий",
                                     reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
        else:
            if (await state.get_data())['type'] == "oper":
                if oper == "topup":
                    buttons.append([types.InlineKeyboardButton(text='\U00002705 Подтвердить',
                                                           callback_data=BalanceManageCallback(action="create_request", operation=oper, way=way, sum=message.text).pack())])
                else:
                    buttons.append([types.InlineKeyboardButton(text='\U00002705 Подтвердить',
                                                           callback_data=BalanceManageCallback(action="enter_requisites", operation=oper, way=way, sum=message.text).pack())])
                buttons.append([types.InlineKeyboardButton(text='\U0000267B Изменить',
                                                           callback_data=BalanceManageCallback(operation=oper, from_where="main", action="choose_way").pack())])
                await message.answer(f"<b>Подтвердите правильность способа и суммы</b>"
                                     f"\n\nСумма {lineoper} - <b>{int(message.text)}₽</b>"
                                     f"\nСпособ {lineoper} - <b>{lineway}</b>",
                                     reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
            elif (await state.get_data())['type'] == "bet":
                await ch().bet_sum_checker(message, game, int(message.text), "check_bet")
            elif (await state.get_data())['type'] == "admin":
                buttons.append([types.InlineKeyboardButton(text="\U00002705 Подтвердить",
                                                           callback_data=AdminManageCallback(action="change_balance", user_id=user_id, key=way, sum=message.text).pack())])
                buttons.append([types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                           callback_data=AdminManageCallback(action="user_balance", key="main", user_id=user_id).pack())])
                await message.answer(f"<b>Подтвердите правильность данных:\n\n"
                                     f"Пользователь - <code>{user_id}</code>\n"
                                     f"{text_confirm}{message.text}₽</b>",
                                     reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
    except:
        logs.info(
            f"User {message.from_user.id} tried to enter sum of {(await state.get_data())['type']} - {message.text}")
        buttons.append([b_enter_again])
        buttons.append([await b().BT_Lk()])
        await message.answer("<b>Неверный формат числа. </b>\n\nВыберите одно из действий",
                             reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.clear()


@router.message(F.text == "\U0001F464 Личный кабинет")
async def account(message):
    await ch().data_checker(message.from_user)
    text, keyboard = await b().KBT_Account(message.from_user.id)
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text == "\U0001F4AC Поддержка")
async def main_rules(message):
    await message.delete()
    await message.answer("\U00002139 В случае возникновения проблем с использованием "
                         "бота вы можете связаться с поддержкой используя кнопку ниже:",
                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                             [await b().BT_Support()],
                             [await b().BT_Close()]
                         ]))


@router.message(F.text.in_({"\U00002139 Меню", "\U00002B05 В меню", "\U0001F680 Начать пользование"}))
async def main(message: types.Message):
    await message.answer("\U0001F4CD Вы перешли в меню",
                         reply_markup=await b().KB_Menu())


@router.message(F.text.in_({"\U0001F3AE Игры", "\U00002B05 К играм", "\U00002B05 Назад"}))
async def main_games(message):
    await message.answer("\U0001F914 Выберите тип игры",
                         reply_markup=await b().KB_MainGames())


@router.message(F.text == "\U0001F4BB Онлайн")
async def main_games(message):
    await message.answer("\U0001F3AF Выберите игру",
                         reply_markup=await b().KB_OnlineGames())


@router.message(F.text == "\U0001F680 Быстрая игра")
async def main_games(message):
    await message.answer("\U0001F3AF Выберите игру",
                         reply_markup=await b().KB_OfflineGames())


@router.message(F.text == "\U00002139 Справка")
async def info_bot(message):
    await message.answer(t.m_main_info,
                         reply_markup=await b().KB_Info())


@router.message(F.text.in_({"\U0001F4AC Комиссия", "\U0001F4AC Алгоритмы", "\U0001F4AC Правила"}))
async def que_answ(message):
    await message.delete()
    await message.answer(t.dct_que_answ[message.text],
                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[await b().BT_Close()]]))


@router.message(F.text.in_({"\U0001F93A Дуэль", "\U0001F3B2 Русская рулетка",
                            "\U0001F451 Королевская битва", "\U0001F3B3 Боулинг",
                            "\U0001F3B2 Бросить кубик", "\U0001F3B0 Крутить рулетку"}))
async def online_game_bet(message):
    text, keyboard = await b().KBT_GameBet(message.text)
    await message.answer(text, reply_markup=keyboard)

