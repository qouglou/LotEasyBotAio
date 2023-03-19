from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from bot.configs import conf
from bot.configs.logs_config import logs

from bot.callback_factory import AdminManageCallback
from bot.middlewares.admin_valid_check import AdminValidCallMiddleware, AdminValidMsgMiddleware
from bot.middlewares.ban_rules_check import BanRulesMsgMiddleware

from bot.db_conn_create import db

from bot.fsm import FSM
from bot.templates.buttons import ButtonsTg as b
from bot.templates.messages import Messages as msg

router = Router()
router.callback_query.middleware(AdminValidCallMiddleware())
router.message.middleware(AdminValidMsgMiddleware())
router.message.middleware(BanRulesMsgMiddleware())


# Вызов основной админской панели BPManager через команду
@router.message(Command("bpm"))
async def adm_manage_cmd(message: types.Message):
        text, keyboard = await b().KBT_Bpmanag(message.from_user.id)
        await message.answer(text, reply_markup=keyboard)


# Вызов основной админской панели BPManager через callback. Запрос типа main_bpmanag
@router.callback_query(AdminManageCallback.filter(F.action == "open_main"))
async def adm_manage_call(call: types.CallbackQuery):
        text, keyboard = await b().KBT_Bpmanag(call.from_user.id)
        await call.message.edit_text(text=text, reply_markup=keyboard)


# Админский обработчик запроса подтверждения транзакции. Запрос типа (adm)(chk)_accure_тип транзакции(05)_
# айди транзакции
@router.callback_query(AdminManageCallback.filter(F.action == "check_oper"))
@router.callback_query(AdminManageCallback.filter(F.action == "confirm_oper"))
async def change_trans_type(call: types.CallbackQuery, callback_data: AdminManageCallback):
    if await db.adm_lvl_check(call.from_user.id) > conf.junior_lvl:
        if callback_data.action == "confirm_oper":
            if callback_data.operation == "topup":
                await db.adm_topup_true(callback_data.id_oper)
            elif callback_data.operation == "withd":
                await db.adm_withd_true(callback_data.id_oper)
            logs.warning(f"Admin {call.from_user.id} confirm transaction of {callback_data.operation} №{callback_data.id_oper}")
            await call.message.edit_text(text=f"<b>Транзакция №{callback_data.id_oper} успешно подтверждена!</b>",
                                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                            [types.InlineKeyboardButton(text='\U0000267B Другая транзакция',
                                                                        callback_data=AdminManageCallback(action="choose_type").pack())],
                                            [await b().BT_AdmLk()]
                                        ]))
        elif callback_data.action == "check_oper":
            if callback_data.operation == "topup":
                way = "пополнения"
            elif callback_data.operation == "withd":
                way = "вывода"
            await call.message.edit_text(text=f"<b>Вы хотите подтвердить транзакцию {way} №{callback_data.id_oper}?</b>",
                                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                            [types.InlineKeyboardButton(text='\U00002705 Да',
                                                                        callback_data=AdminManageCallback(action="confirm_oper", operation=callback_data.operation, id_oper=callback_data.id_oper).pack())],
                                            [await b().BT_AdmLk()]
                                        ]))
    else:
        logs.warning(f"Admin {call.from_user.id} with access {await db.adm_lvl_check(call.from_user.id)} tried to get "
                        f"access to admin functionality with call - {call}")
        await msg().no_access(call, "1 (Middle)", "call")
    await call.answer()


# Админский обработчик с выбором типа желаемой транзакции
@router.callback_query(AdminManageCallback.filter(F.action == "choose_type"))
async def choose_trans_type(call: types.CallbackQuery):
    await call.message.edit_text(text="<b>Выберите тип транзакции</b>", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text='Пополнение', callback_data=AdminManageCallback(action="select_oper", operation="topup").pack()),
             types.InlineKeyboardButton(text='Вывод', callback_data=AdminManageCallback(action="select_oper", operation="withd").pack())],
            [await b().BT_AdmLk("\U00002B05")]
        ]))
    await call.answer()


@router.callback_query(AdminManageCallback.filter(F.action == "change_balance"))
async def balance_change(call: types.CallbackQuery, callback_data: AdminManageCallback):
    if await db.adm_lvl_check(call.from_user.id) > conf.master_lvl:
        if callback_data.key == "nul":
            await db.adm_nul_balance(callback_data.user_id)
            await call.message.edit_text(text=f"<b>Баланс пользователя <code>{callback_data.user_id}</code> обнулен</b>",
                                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                            [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                                        callback_data=AdminManageCallback(action="user_info", user_id=callback_data.user_id).pack())],
                                            [await b().BT_AdmLk()]
                                        ]))
        elif callback_data.key in ("add", "rem"):
            if callback_data.key == "add":
                await db.set_topup_balance(callback_data.user_id, callback_data.sum)
                text_act = "пополнен"
            elif callback_data.key == "rem":
                if callback_data.sum > await db.get_user_balance(callback_data.user_id):
                    return await call.message.edit_text(text=f"<b>Нельзя уменьшить баланс пользователя <code>{callback_data.user_id}</code> на сумму, "
                        f"превышающую его баланс - {int(await db.get_user_balance(callback_data.user_id))}₽</b>",
                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                            [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                        callback_data=AdminManageCallback(action="user_balance", user_id=callback_data.user_id, key="rem").pack())],
                            [await b().BT_AdmLk()]
                        ]))
                else:
                    await db.set_withdraw_balance(callback_data.user_id, callback_data.sum)
                    text_act = "уменьшен"
            await call.message.edit_text(text=f"<b>Баланс пользователя <code>{callback_data.user_id}</code> {text_act} на {callback_data.sum}₽</b>",
                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                callback_data=AdminManageCallback(action="user_info", user_id=callback_data.user_id).pack())],
                    [await b().BT_AdmLk()]
                ]))
        elif callback_data.key == "set":
            await db.adm_set_balance(callback_data.user_id, callback_data.sum)
            await call.message.edit_text(text=f"<b>Новый баланс пользователя <code>{callback_data.user_id}</code> - {callback_data.sum}₽</b>",
                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                callback_data=AdminManageCallback(action="user_info", user_id=callback_data.user_id).pack())],
                    [await b().BT_AdmLk()]
                ]))
    else:
        await msg().no_access(call, "3 (Superuser)", "call")
    await call.answer()


@router.callback_query(AdminManageCallback.filter(F.action == "user_balance"))
async def balance_change_check(call: types.CallbackQuery, callback_data: AdminManageCallback, state: FSMContext):
    if await db.adm_lvl_check(call.from_user.id) > conf.master_lvl:
        if callback_data.key == "main":
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="\U0001F4C8 Добавить",
                                               callback_data=AdminManageCallback(action="user_balance", key="add", user_id=callback_data.user_id).pack()),
                    types.InlineKeyboardButton(text="\U0001F4C9 Снять",
                                               callback_data=AdminManageCallback(action="user_balance", key="rem", user_id=callback_data.user_id).pack())],
                [
                    types.InlineKeyboardButton(text="\U0001F4A3 Обнулить",
                                               callback_data=AdminManageCallback(action="user_balance", key="nul", user_id=callback_data.user_id).pack()),
                    types.InlineKeyboardButton(text="\U0001F4DD Изменить",
                                               callback_data=AdminManageCallback(action="user_balance", key="set", user_id=callback_data.user_id).pack())
                ],
                [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                            callback_data=AdminManageCallback(action="user_info", user_id=callback_data.user_id).pack())],
                [await b().BT_AdmLk()]
            ])
            await call.message.edit_text(text=f"<b>Выберите действие с балансом пользователя <code>{callback_data.user_id}</code></b>",
                                         reply_markup=keyboard)
        else:
            if callback_data.key in ("add", "rem"):
                if callback_data.operation is None:
                    if callback_data.key == "add":
                        text_act = "увеличения"
                    else:
                        text_act = "уменьшения"
                    await call.message.edit_text(text=f"<b>Выберите сумму {text_act} баланса пользователя <code>{callback_data.user_id}</code></b>",
                        reply_markup=await b().KB_Sum("admin", callback_data.user_id, callback_data.key))
                else:
                    if callback_data.key == "add":
                        text_act = "добавления"
                    else:
                        text_act = "уменьшения"
                    await call.message.edit_text(text=f"<b>Введите сумму {text_act} баланса пользователя <code>{callback_data.user_id}</code></b>")
                    await state.update_data(type="admin", way=callback_data.key, user_id=callback_data.user_id)
                    await state.set_state(FSM.other_sum)
            elif callback_data.key == "nul":
                await call.message.edit_text(text=f"<b>Вы действительно хотите обнулить баланс пользователя <code>{callback_data.user_id}</code>?</b>",
                                             reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                        [types.InlineKeyboardButton(text="\U0001F512 Да",
                                                    callback_data=AdminManageCallback(action="change_balance", key="nul", user_id=callback_data.user_id).pack())],
                        [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                    callback_data=AdminManageCallback(action="user_balance", user_id=callback_data.user_id, key="main").pack())],
                        [await b().BT_AdmLk()]
                    ]))
            elif callback_data.key == "set":
                await call.message.edit_text(text=f"<b>Введите новый баланс пользователя <code>{callback_data.user_id}</code></b>")
                await state.update_data(type="admin", way="set", user_id=callback_data.user_id)
                await state.set_state(FSM.other_sum)
    else:
        await msg().no_access(call, "3 (Superuser)", "call")
    await call.answer()


@router.callback_query(AdminManageCallback.filter(F.action == "admin_list"))
async def admin_list(call: types.CallbackQuery):
    if await db.adm_lvl_check(call.from_user.id) == conf.superuser_lvl:
        N = await db.get_admin_lines()
        adm_info_line = "<b>\U0001F4D6 Список администраторов:</b>"
        while N > 0:
            id_adm, user_id, valid, access_lvl = [x for x in await db.adm_list_info(N)]
            if valid:
                valid_line = "\U00002705"
            else:
                valid_line = "\U0000274C"
            adm_info_line += f"\n\n<b>№{id_adm} - <code>{user_id}</code>\nПолномочия - {valid_line}\nУровень - {access_lvl}</b>"
            N -= 1
        buttons = [
            [types.InlineKeyboardButton(text="Просмотр админа", callback_data=AdminManageCallback(action="choose_admin").pack())],
            [types.InlineKeyboardButton(text="Добавить админа", callback_data=AdminManageCallback(action="add_admin_check").pack())],
            [await b().BT_AdmLk()]
        ]
        await call.message.edit_text(text=adm_info_line, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
    else:
        await msg().no_access(call, "3 (Superuser)", "call")
    await call.answer()


@router.callback_query(AdminManageCallback.filter(F.action == "add_admin_check"))
@router.callback_query(AdminManageCallback.filter(F.action == "choose_admin"))
@router.callback_query(AdminManageCallback.filter(F.action == "choose_user"))
async def enter_id(call: types.CallbackQuery, callback_data: AdminManageCallback, state: FSMContext):
    if callback_data.action == "choose_user":
        await call.message.edit_text(text="<b>Введите ник или айди пользователя</b>")
        await state.update_data(id_adm=call.from_user.id, type="user")
    elif callback_data.action == "choose_admin":
        await call.message.edit_text(text="<b>Введите айди администратора</b>")
        await state.update_data(id_adm=call.from_user.id, type="admin")
    elif callback_data.action == "add_admin_check":
        await call.message.edit_text(text="<b>Введите айди пользователя</b>")
        await state.update_data(id_adm=call.from_user.id, type="add_admin_check")
    await state.set_state(FSM.enter_id_user)
    await call.answer()


@router.callback_query(AdminManageCallback.filter(F.action == "check_ban"))
async def check_block_user(call: types.CallbackQuery, callback_data: AdminManageCallback):
    if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
        if await db.get_ban(callback_data.user_id):
            text_act = "разблокировать"
        else:
            text_act = "заблокировать"
        await call.message.edit_text(text=f"<b>Вы действительно хотите {text_act} пользователя <code>{callback_data.user_id}</code>?</b>",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="\U0001F512 Да",
                                            callback_data=AdminManageCallback(action="ban_user", user_id=callback_data.user_id).pack())],
                [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                            callback_data=AdminManageCallback(action="user_info", user_id=callback_data.user_id).pack())],
                [await b().BT_AdmLk()]
            ]))
    else:
        await msg().no_access(call, "2 (Master)", "call")
    await call.answer()


@router.callback_query(AdminManageCallback.filter(F.action == "ban_user"))
async def block_user(call: types.CallbackQuery, callback_data: AdminManageCallback):
    if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
        if await db.get_ban(callback_data.user_id):
            action = False
            text_act = "разблокирован"
        else:
            action = True
            text_act = "заблокирован"
        if await db.adm_check(callback_data.user_id) and await db.adm_lvl_check(callback_data.user_id) > await db.adm_lvl_check(call.from_user.id):
            await call.message.edit_text(
                text=f"<b>Вы не можете заблокировать админа выше вас по рангу</b>",
                reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                callback_data=AdminManageCallback(action="user_info",
                                                                                  user_id=callback_data.user_id).pack())],
                    [await b().BT_AdmLk()]
                ]))
        else:
            await db.adm_ban_user(callback_data.user_id, action)
            await call.message.edit_text(text=f"<b>Пользователь <code>{callback_data.user_id}</code> успешно {text_act}!</b>",
                                         reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                            [types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                                        callback_data=AdminManageCallback(action="user_info", user_id=callback_data.user_id).pack())],
                                            [await b().BT_AdmLk()]
                                        ]))
    else:
        await msg().no_access(call, "2 (Master)", "call")
    await call.answer()


@router.callback_query(AdminManageCallback.filter(F.action == "admin_info"))
@router.callback_query(AdminManageCallback.filter(F.action == "user_info"))
async def user_info(call: types.CallbackQuery, callback_data: AdminManageCallback):
    if callback_data.action == "user_info":
        await adm_user_info(call, callback_data.user_id, "call")
    else:
        await adm_adm_info(call, callback_data.user_id, "call")
    await call.answer()


@router.callback_query(AdminManageCallback.filter(F.action == "add_admin"))
async def user_info(call: types.CallbackQuery, callback_data: AdminManageCallback):
    if await db.adm_lvl_check(call.from_user.id) == conf.superuser_lvl:
        await db.adm_add_admin(callback_data.user_id, call.from_user.id)
        await call.message.edit_text(text=f"<b>Пользователь <code>{callback_data.user_id}</code> назначен администратором {conf.junior_lvl} уровня\n\n"
                                          f"Повысить его до следующих уровней можно через подробную панель информации об администраторе</b>",
                                     reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                         [types.InlineKeyboardButton(text='\U00002B05 К списку', callback_data=AdminManageCallback(action="admin_list").pack())],
                                         [await b().BT_AdmLk()]
                                     ]))
    else:
        await msg().no_access(call, "3 (Superuser)", "call")
    await call.answer()


async def add_admin_check(message):
    buttons = []
    if message.text.isdigit() and await db.get_user_exists(message.text):
        if not await db.adm_check(message.text):
            text_line = f"<b>Вы действительно хотите сделать администратором пользователя <code>{message.text}</code>?</b>"
            buttons.append(
                [types.InlineKeyboardButton(text="\U00002705 Да", callback_data=AdminManageCallback(action="add_admin", user_id=message.text).pack())]
            )
        else:
            text_line = "<b>Данный пользователь уже является администратором</b>"
            buttons.append(
                [types.InlineKeyboardButton(text="\U0000267B Ввести заново", callback_data=AdminManageCallback(action="add_admin_check").pack())]
            )
    else:
        text_line = "<b>Данный пользователь не найден</b>"
        buttons.append([
            types.InlineKeyboardButton(text="\U0000267B Ввести заново", callback_data=AdminManageCallback(action="add_admin_check").pack())]
        )
    buttons.append(
        [types.InlineKeyboardButton(text="\U00002B05 Назад", callback_data=AdminManageCallback(action="admin_list").pack())]
        )
    buttons.append([await b().BT_AdmLk()])
    await message.answer(text=text_line, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(AdminManageCallback.filter(F.action == "remove_admin_check"))
@router.callback_query(AdminManageCallback.filter(F.action == "return_admin_check"))
@router.callback_query(AdminManageCallback.filter(F.action == "upgrade_admin_check"))
@router.callback_query(AdminManageCallback.filter(F.action == "demote_admin_check"))
async def remove_admin_check(call: types.CallbackQuery, callback_data: AdminManageCallback):
    text_admin_action = {
        "remove_admin_check": f"<b>Вы действительно хотите снять полномочия с администратора <code>{callback_data.user_id}</code>?</b>",
        "return_admin_check": f"<b>Вы действительно хотите дать полномочия администратору <code>{callback_data.user_id}</code>?</b>",
        "upgrade_admin_check": f"<b>Вы действительно хотите повысить администратора <code>{callback_data.user_id}</code>?</b>",
        "demote_admin_check": f"<b>Вы действительно хотите понизить администратора <code>{callback_data.user_id}</code>?</b>"
    }[callback_data.action]
    await call.message.edit_text(text=text_admin_action, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="\U00002705 Да", callback_data=AdminManageCallback(action=callback_data.action[:-6], user_id=callback_data.user_id).pack())],
        [types.InlineKeyboardButton(text="\U00002B05 Назад", callback_data=AdminManageCallback(action="admin_info", user_id=callback_data.user_id).pack())],
        [await b().BT_AdmLk()]
    ]))


@router.callback_query(AdminManageCallback.filter(F.action == "remove_admin"))
@router.callback_query(AdminManageCallback.filter(F.action == "return_admin"))
@router.callback_query(AdminManageCallback.filter(F.action == "upgrade_admin"))
@router.callback_query(AdminManageCallback.filter(F.action == "demote_admin"))
async def remove_admin_check(call: types.CallbackQuery, callback_data: AdminManageCallback):
    if await db.adm_lvl_check(call.from_user.id) == conf.superuser_lvl:
        if callback_data.action == "remove_admin":
            if await db.adm_valid_check(callback_data.user_id):
                await db.set_adm_valid(callback_data.user_id, False)
                text_info = f"<b>Права администратора у пользователя <code>{callback_data.user_id}</code> убраны</b>"
            else:
                text_info = f"<b>У пользователя <code>{callback_data.user_id}</code> нет прав администратора</b>"
        elif callback_data.action == "return_admin":
            if not await db.adm_valid_check(callback_data.user_id):
                await db.set_adm_valid(callback_data.user_id, True)
                text_info = f"<b>Пользователь <code>{callback_data.user_id}</code> снова действующий администратор</b>"
            else:
                text_info = f"<b>Пользователь <code>{callback_data.user_id}</code> и так является действующим администратором</b>"
        elif callback_data.action == "upgrade_admin":
            if await db.adm_lvl_check(callback_data.user_id) in (conf.junior_lvl, conf.middle_lvl, conf.master_lvl):
                await db.set_adm_lvl(callback_data.user_id, (await db.adm_lvl_check(callback_data.user_id)) + 1)
                text_info = f"<b>Пользователь <code>{callback_data.user_id}</code> повышен до уровня {await db.adm_lvl_check(callback_data.user_id)}</b>"
            else:
                text_info = f"<b>У пользователя <code>{callback_data.user_id}</code> и так максимальный уровень</b>"
        elif callback_data.action == "demote_admin":
            if await db.adm_lvl_check(callback_data.user_id) in (conf.middle_lvl, conf.master_lvl, conf.superuser_lvl):
                await db.set_adm_lvl(callback_data.user_id, (await db.adm_lvl_check(callback_data.user_id)) - 1)
                text_info = f"<b>Пользователь <code>{callback_data.user_id}</code> понижен до уровня {await db.adm_lvl_check(callback_data.user_id)}</b>"
            else:
                text_info = f"<b>У пользователя <code>{callback_data.user_id}</code> и так минимальный уровень</b>"
        await call.message.edit_text(text=text_info, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="\U00002B05 Назад", callback_data=AdminManageCallback(action="admin_info", user_id=callback_data.user_id).pack())],
            [await b().BT_AdmLk()]
        ]))
    else:
        await msg().no_access(call, "3 (Superuser)", "call")
    await call.answer()


async def adm_adm_info(object, user_id, type):
    if user_id.isdigit() and await db.adm_check(user_id):
        id, adm_id, inviter, time_invite, valid, access_lvl = [x for x in await db.adm_adm_info(user_id)]
        time_invite = str(time_invite)
        buttons = []
        if valid:
            valid_line = "\U00002705"
        else:
            valid_line = "\U0000274C"
        adm_info_line = f"<b>Информация об администраторе:</b>\n\n" \
                        f"<b>ID администратора - </b><code>{adm_id}</code>\n" \
                        f"<b>Назначен администратором - </b><code>{inviter}</code>\n" \
                        f"<b>Время назначения - </b>{time_invite[:19]}\n" \
                        f"<b>Действующий - </b>{valid_line}\n" \
                        f"<b>Уровень - </b>{access_lvl}"
        if await db.adm_lvl_check(object.from_user.id) == conf.superuser_lvl:
            if valid:
                buttons.append([types.InlineKeyboardButton(text="\U0001F4DB Снять полномочия",
                                                   callback_data=AdminManageCallback(action="remove_admin_check",
                                                                                     user_id=adm_id).pack())])
            else:
                buttons.append([types.InlineKeyboardButton(text="\U0001F4DB Вернуть полномочия",
                                                   callback_data=AdminManageCallback(action="return_admin_check",
                                                                                     user_id=adm_id).pack())])
            if access_lvl == conf.junior_lvl:
                buttons.append([types.InlineKeyboardButton(text="\U000023EB Повысить",
                                                   callback_data=AdminManageCallback(action="upgrade_admin_check",
                                                                                     user_id=adm_id).pack())])
            elif access_lvl == conf.superuser_lvl:
                buttons.append([types.InlineKeyboardButton(text="\U000023EC Понизить",
                                                   callback_data=AdminManageCallback(action="demote_admin_check",
                                                                                     user_id=adm_id).pack())])
            else:
                buttons.append([types.InlineKeyboardButton(text="\U000023EB Повысить",
                                                   callback_data=AdminManageCallback(action="upgrade_admin_check",
                                                                                     user_id=adm_id).pack())])
                buttons.append([types.InlineKeyboardButton(text="\U000023EC Понизить",
                                                   callback_data=AdminManageCallback(action="demote_admin_check",
                                                                                     user_id=adm_id).pack())])
            buttons.append([types.InlineKeyboardButton(text="\U00002B05 К списку",
                                                   callback_data=AdminManageCallback(action="admin_list").pack())])
        buttons.append([await b().BT_AdmLk()])
        if type == "message":
            await object.answer(text=adm_info_line, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
        else:
            await object.message.edit_text(text=adm_info_line, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
    else:
        await object.answer(text=F"<b>Администратора с данным ID не существует</b>",
                               reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                   [types.InlineKeyboardButton(text="\U0000267B Ввести заново",
                                                               callback_data=AdminManageCallback(action="choose_admin").pack())],
                                   [await b().BT_AdmLk()]
                               ]))


async def adm_user_info(object, user_id, type):
    adm_id = object.from_user.id
    if user_id.isdigit() and await db.get_user_exists(user_id) or await db.get_user_exists(user_id,
                                                                                           "username ILIKE"):
        if user_id.isdigit():
            key = "user_id ="
        else:
            key = "username ILIKE"
        id_sys, user_id, join_date, balance, name, lastname, username, rules_acc, ban, bot_blocked = [x for x in
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
        if bot_blocked:
            bot_blocked_info = "\U00002705"
        else:
            bot_blocked_info = "\U0000274C"
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
                                                       callback_data=AdminManageCallback(action="user_checker", user_id=user_id).pack())])
            if await db.adm_lvl_check(adm_id) > conf.middle_lvl:
                if await db.get_ban(user_id):
                    text_act = "\U0000274E Разблокировать"
                else:
                    text_act = "\U0000274C Заблокировать"
                buttons.append(
                    [types.InlineKeyboardButton(text=text_act, callback_data=AdminManageCallback(action="check_ban", user_id=user_id).pack())])
                if await db.adm_lvl_check(adm_id) > conf.master_lvl:
                    buttons.append([types.InlineKeyboardButton(text="\U0001F4DD Изменить баланс",
                                                               callback_data=AdminManageCallback(action="user_balance", user_id=user_id, key="main").pack())])
        buttons.append([types.InlineKeyboardButton(text="\U0000267B Другой пользователь",
                                                   callback_data=AdminManageCallback(action="choose_user").pack())])
        buttons.append([await b().BT_AdmLk()])
        if type == "message":
            await object.answer(text=f"<b>Данные о пользователе:\n\n"
                                     f"ID - </b><code>{user_id}</code>\n"
                                     f"<b>Имя -</b> {name}{lastname_info}<b>Баланс -</b> {format(balance, '.0f')}₽\n"
                                     f"<b>Дата регистрации -</b> {join_date[:10]}\n<b>Правила - {rules_info}\n"
                                     f"Заблокировал бота - {bot_blocked_info}\n"
                                     f"Наличие бана - {ban_info}</b>",
                                   reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
        else:
            await object.message.edit_text(text=f"<b>Данные о пользователе:\n\n"
                                                f"ID - </b><code>{user_id}</code>\n"
                                                f"<b>Имя -</b> {name}{lastname_info}<b>Баланс -</b> {format(balance, '.0f')}₽\n"
                                                f"<b>Дата регистрации -</b> {join_date[:10]}\n<b>Правила - {rules_info}\n"
                                                f"Заблокировал бота - {bot_blocked_info}\n"
                                                f"Наличие бана - {ban_info}</b>",
                                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
    else:
        await object.answer(text="<b>Данный пользователь не найден</b>",
                               reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                   [types.InlineKeyboardButton(text="\U0000267B Ввести заново",
                                                               callback_data=AdminManageCallback(action="choose_user").pack())],
                                   [await b().BT_AdmLk()]
                               ]))


@router.message(FSM.enter_id_user)
async def get_id_trans(message: types.Message, state: FSMContext):
    if (await state.get_data())['type'] == "user":
        await adm_user_info(message, message.text, "message")
    elif (await state.get_data())['type'] == "admin":
        await adm_adm_info(message, message.text, "message")
    elif (await state.get_data())['type'] == "add_admin_check":
        await add_admin_check(message)
    await state.clear()


# Админский обработчик ручного ввода номера транзакции. Запрос типа accure_тип транзакции(05)
@router.callback_query(AdminManageCallback.filter(F.action == "select_oper"))
async def accure_trans(call: types.CallbackQuery, callback_data: AdminManageCallback, state: FSMContext):
    if callback_data.operation == "topup":
        await call.message.edit_text(text="<b>Введите ID пополнения</b>")
    elif callback_data.operation == "withd":
        await call.message.edit_text(text="<b>Введите ID вывода</b>")
    await state.update_data(id_adm=call.from_user.id, trans_type=callback_data.operation)
    await state.set_state(FSM.accure_id_trans)
    await call.answer()


# Админский обработчик подтверждения смены способа вывода. Запрос типа chk_withd_change_way_айди вывода
@router.callback_query(AdminManageCallback.filter(F.action == "change_way"))
async def change_withd_way(call: types.CallbackQuery, callback_data: AdminManageCallback):
    if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
        if await db.get_withd_way(callback_data.id_oper) == "bank":
            button_another_way = types.InlineKeyboardButton(text="QIWI",
                                                            callback_data=AdminManageCallback(action="change_requisites", id_oper=callback_data.id_oper, old_way="bank", new_way="qiwi").pack())
            way_withd_write = "Банковская карта"
        elif await db.get_withd_way(callback_data.id_oper) == "qiwi":
            button_another_way = types.InlineKeyboardButton(text="Банковская карта",
                                                            callback_data=AdminManageCallback(action="change_requisites", id_oper=callback_data.id_oper, old_way="qiwi", new_way="bank").pack())
            way_withd_write = "QIWI"
        await call.message.edit_text(text=f"<b>Текущий способ вывода транзакции №{callback_data.id_oper} - {way_withd_write}"
                                    "\n\nВозможность изменить способ вывода на:</b>",
                                    reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                        [button_another_way],
                                        [await b().BT_AdmLk()]
                                    ]))
    else:
        logs.warning(
            f"Admin {call.from_user.id} with access {await db.adm_lvl_check(call.from_user.id)} tried to get "
            f"access to admin functionality with call - {call}")
        await msg().no_access(call, "2 (Master)", "call")
    await call.answer()


# Админский обработчик ручного ввода новых реквизитов. Запрос типа rqs_withd_change_способ вывода(04)_старый способ(04)
@router.callback_query(AdminManageCallback.filter(F.action == "change_requisites"))
async def get_new_req(call: types.CallbackQuery, callback_data: AdminManageCallback, state: FSMContext):
    if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
        await call.message.edit_text(text="<b>Введите новые реквизиты</b>")
        await state.update_data(id_adm=call.from_user.id, new_way=callback_data.new_way,
                                old_way=await db.get_withd_way(callback_data.id_oper), with_id=callback_data.id_oper)
        await state.set_state(FSM.adm_new_requis)
    else:
        logs.warning(
            f"Admin {call.from_user.id} with access {await db.adm_lvl_check(call.from_user.id)} tried to get "
            f"access to admin functionality with call - {call}")
        await msg().no_access(call, "2 (Master)", "call")
    await call.answer()


# Админская панель отображения измененных данных вывода
@router.message(FSM.adm_new_requis)
async def get_id_trans(message: types.Message, state: FSMContext):
    data = await state.get_data()
    buttons = []
    adm_id = data['id_adm']
    with_id = int(data['with_id'])
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
                                                       callback_data=AdminManageCallback(action="new_requisites", id_oper=with_id, new_way=data['new_way'], new_requisites=new_req).pack())])

            buttons.append([await b().BT_AdmLk()])
            await message.answer(f"<b>Желаемые изменения: \n\nТранзакция №{with_id}\n"
                                 f"{about_new_way}Новые реквизиты - {new_req}</b>",
                                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
        except:
            buttons.append([types.InlineKeyboardButton(text="\U0000267B Ввести заново",
                                                       callback_data=AdminManageCallback(action="change_requisites", id_oper=with_id, old_way=data['old_way'], new_way=data['new_way']).pack())])
            buttons.append([await b().BT_AdmLk()])
            await message.answer("<b>Неверные реквизиты\n\nВыберите одно из действий:</b>",
                                 reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
    else:
        logs.warning(
            f"Admin {message.from_user.id} with access {await db.adm_lvl_check(adm_id)} tried to get "
            f"access to admin functionality with message - {message}")
        await msg().no_access(message, "2 (Master)", "message")
    await state.clear()


# Админский обработчик изменения транзакции вывода. Запрос типа adm_withd_change_способ(04)_
# айди транзакции(10)_новые реквизиты
@router.callback_query(AdminManageCallback.filter(F.action == "new_requisites"))
async def change_withd_way(call: types.CallbackQuery, callback_data: AdminManageCallback):
    if await db.adm_lvl_check(call.from_user.id) > conf.middle_lvl:
        logs.warning(
            f"Admin {call.from_user.id} change requisites from {await db.get_requisites(callback_data.id_oper)} to {callback_data.new_requisites}")
        await db.adm_update_withd(callback_data.id_oper, callback_data.new_way, callback_data.new_requisites)
        if callback_data.new_way == "bank":
            new_way_w = "Банковская карта"
        else:
            new_way_w = "QIWI"
        await call.message.edit_text(text=f"<b>Текущая информация: \n\nТранзакция №{callback_data.id_oper}\nСпособ - {new_way_w}"
            f"\nРеквизиты - {callback_data.new_requisites}</b>", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text='\U0000267B Другая транзакция',
                                            callback_data=AdminManageCallback(action="choose_type").pack())],
                [await b().BT_AdmLk()]
            ]))
    else:
        logs.warning(
            f"Admin {call.from_user.id} with access {await db.adm_lvl_check(call.from_user.id)} tried to get "
            f"access to admin functionality with call - {call}")
        await msg().no_access(call, "2 (Master)", "call")
    await call.answer()


# Админская панель отображения транзакций
@router.message(FSM.accure_id_trans)
async def get_id_trans(message: types.Message, state: FSMContext):
    data = await state.get_data()
    buttons = []
    id_adm = data['id_adm']
    trans_type = data['trans_type']
    b_adm_trans = types.InlineKeyboardButton(text='\U0000267B Другая транзакция',
                                             callback_data=AdminManageCallback(action="choose_type").pack())
    try:
        if not message.text.isdigit():
            raise
        if 0 < int(message.text) < 100000:
            if trans_type == "topup":
                id_get_trans, user, way, sum, time_cr, accure, done, time_do, oper, requisites = [str(x) for x
                                                                                                  in
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
                                                               callback_data=AdminManageCallback(action="confirm_oper", id_oper=id_get_trans, operation="topup").pack())])
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
                                     reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
            elif trans_type == "withd":
                if done == "False" and await db.adm_lvl_check(id_adm) > conf.junior_lvl:
                    buttons.append([types.InlineKeyboardButton(text='\U00002705 Подтвердить транзакцию',
                                                               callback_data=AdminManageCallback(action="confirm_oper", id_oper=id_get_trans, operation="withd").pack())])
                    if await db.adm_lvl_check(id_adm) > conf.middle_lvl:
                        buttons.append([types.InlineKeyboardButton(text='\U0000267B Изменить способ',
                                                                   callback_data=AdminManageCallback(action="change_way", id_oper=id_get_trans).pack())])
                        buttons.append([types.InlineKeyboardButton(text='\U0000267B Изменить реквизиты',
                                                                   callback_data=AdminManageCallback(action="change_requisites", id_oper=id_get_trans, new_way=way).pack())])
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
                                     reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
        else:
            raise
    except:
        buttons.append([b_adm_trans])
        buttons.append([await b().BT_AdmLk()])
        await message.answer(f"<b>Транзакция с таким номером не найдена.</b>"
                             "\n\nВыберите одно из действий",
                             reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.clear()
