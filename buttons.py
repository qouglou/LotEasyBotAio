from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import conf
from db import BotDB as db
from callback_factory import BalanceManageCallback, AdminManageCallback

bot = Bot(token=conf.TOKEN)
dp = Dispatcher(storage=MemoryStorage())


db = db('lotEasy.db')


class ButtonsTg:

    async def KB_Start(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [types.KeyboardButton(text="\U0001F680 Начать пользование")]
        ])

    async def KB_Menu(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, keyboard=
                                         [
                                             [types.KeyboardButton(text="\U0001F464 Личный кабинет")],
                                             [types.KeyboardButton(text="\U0001F3AE Игры")],
                                             [types.KeyboardButton(text="\U00002139 Справка")]
                                         ])

    async def KB_Sum(self, type, key, way="", from_where=""):
        async def BT_sum(type, key, way, emoji, sum):
            if type == "game":
                button_sum = types.InlineKeyboardButton(text=f"{emoji} {sum} ₽", callback_data=BalanceManageCallback(action="check_bet", game=key, sum=sum).pack())
            elif type == "oper":
                if key == "topup":
                    button_sum = types.InlineKeyboardButton(text=f"{emoji} {sum} ₽",
                                                  callback_data=BalanceManageCallback(action="create_request", operation=key, way=way, sum=sum).pack())
                else:
                    button_sum = types.InlineKeyboardButton(text=f"{emoji} {sum} ₽",
                                                            callback_data=BalanceManageCallback(
                                                                action="enter_requisites", operation=key, way=way,
                                                                sum=sum).pack())
            elif type == "admin":
                button_sum = types.InlineKeyboardButton(text=f"{emoji} {sum} ₽",
                                                  callback_data=AdminManageCallback(action="change_balance", user_id=key, key=way, sum=sum).pack())
            return button_sum
        buttons = [
            [await BT_sum(type, key, way, "\U0001F4B4", 50), await BT_sum(type, key, way, "\U0001F4B5", 100)],
            [await BT_sum(type, key, way, "\U0001F4B6", 500), await BT_sum(type, key, way, "\U0001F4B0", 1000)]
        ]

        if type == "game":
            if key in ("bowl", "cube", "slot"):
                buttons.append([types.InlineKeyboardButton(text="\U0001F4DD Другая сумма", callback_data=BalanceManageCallback(action="choose_other", operation="bet", game=key).pack())])
            buttons.append([types.InlineKeyboardButton(text="\U00002753 Справка", callback_data=f"que_{key}")])
        elif type == "oper":
            buttons.append([types.InlineKeyboardButton(text="\U0001F4DD Другая сумма",
                                                 callback_data=BalanceManageCallback(action="choose_other", operation=key, way=way).pack())])
            buttons.append([types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                     callback_data=BalanceManageCallback(action="choose_way", operation=key, from_where=from_where).pack())])
        elif type == "admin":
            buttons.append([types.InlineKeyboardButton(text="\U0001F4DD Другая сумма",
                                                 callback_data=AdminManageCallback(action="user_balance", user_id=key, key=way, operation="other").pack())])
            buttons.append([types.InlineKeyboardButton(text="\U00002B05 Назад",
                                                     callback_data=AdminManageCallback(action="user_balance", key="main", user_id=key).pack())])
            buttons.append([await self.BT_AdmLk()])
        return types.InlineKeyboardMarkup(inline_keyboard=buttons)

    async def KBT_GameBet(self, game):
        if game in ("\U0001F451 Королевская битва", "king"):
            game = "king"
            sh_t = "\U0001F451 Шанс мал, но приз огромен!\nУдачи!\n\n<b>Выберите сумму:</b>"
        elif game in ("\U0001F3B2 Русская рулетка", "russ"):
            game = "russ"
            sh_t = "\U0001F3B2 1 на 5, отличный выбор!\nЖелаем вам удачи!\n\n<b>Выберите сумму:</b>"
        elif game in ("\U0001F93A Дуэль", "duel"):
            game = "duel"
            sh_t = "\U0001F93A 1 на 1, 50 на 50, шансы удвоить сумму высоки!\nУдачи!\n\n<b>Выберите сумму:</b>"
        elif game in ("\U0001F3B3 Боулинг", "bowl"):
            game = "bowl"
            sh_t = "\U0001F3B3 Чтож, сыграем в боулинг!\n\n<b>Выберите сумму:</b>"
        elif game in ("\U0001F3B2 Бросить кубик", "cube"):
            game = "cube"
            sh_t = "\U0001F3B2 Старый добрый кубик!\n\n<b>Выберите сумму:</b>"
        elif game in ("\U0001F3B0 Крутить рулетку", "slot"):
            game = "slot"
            sh_t = "\U0001F3B0 Жми на рычаг и испытай свою удачу!\n\n<b>Выберите сумму:</b>"
        return sh_t, await self.KB_Sum("game", game)

    async def KB_MainGames(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, keyboard=[
            [types.KeyboardButton(text="\U0001F680 Быстрая игра")],
            [types.KeyboardButton(text="\U0001F4BB Онлайн")],
            [types.KeyboardButton(text="\U00002B05 В меню")],
        ])

    async def KB_OnlineGames(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, keyboard=[
            [types.KeyboardButton(text="\U0001F93A Дуэль")],
            [types.KeyboardButton(text="\U0001F3B2 Русская рулетка")],
            [types.KeyboardButton(text="\U0001F451 Королевская битва")],
            [types.KeyboardButton(text="\U00002B05 Назад")],
        ])

    async def KB_OfflineGames(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, keyboard=[
            [types.KeyboardButton(text="\U0001F3B3 Боулинг")],
            [types.KeyboardButton(text="\U0001F3B2 Бросить кубик")],
            [types.KeyboardButton(text="\U0001F3B0 Крутить рулетку")],
            [types.KeyboardButton(text="\U00002B05 Назад")],
        ])

    async def KB_Info(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, is_persistent=True, keyboard=[
            [
                types.KeyboardButton(text="\U0001F4AC Комиссия"),
                types.KeyboardButton(text="\U0001F4AC Алгоритмы")
            ],
            [
                types.KeyboardButton(text="\U0001F4AC Правила"),
                types.KeyboardButton(text="\U0001F4AC Поддержка"),
            ],
            [types.KeyboardButton(text="\U00002B05 В меню")]
        ])

    async def ButtonTopupCheck(self, user_id, way_topup, id_pay, msg_id):
        if await db.get_topup_accured(id_pay) == 0:
            await bot.edit_message_text("<b>Транзакция не найдена.</b>\n\nПроверьте перевод еще раз, либо обратитесь к поддержке",
                                        user_id, msg_id, reply_markup=
                                        types.InlineKeyboardMarkup(inline_keyboard=[
                                            [
                                                await self.BT_Support(),
                                            types.InlineKeyboardButton(
                                                text='\U0000267B Проверить еще раз',
                                                callback_data=f"check_topup_{way_topup}_{format(id_pay, '7')}")
                                             ]
                                        ]))
        elif (await db.get_topup_accured(id_pay) == 1) & (
                await db.get_topup_done(id_pay) == 0):
            await db.set_topup_balance(user_id, await db.get_topup_sum(id_pay))
            await db.set_topup_done(id_pay)
            m_success_topup = (f"\U00002705 <b>Транзакция успешно выполнена!</b>"
                               f"\n\n<b>Ваш баланс:</b>\n{int(await db.get_user_balance(user_id))}₽")
            await bot.edit_message_text(m_success_topup, user_id, msg_id,
                                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[await self.BT_Lk(msg_id)]))
        elif await db.get_topup_done(id_pay) == 1:
            await bot.delete_message(user_id, msg_id)
            await bot.send_message(user_id, "<b>Данная транзакция уже выполнена</b>",
                                   reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[await self.BT_Close()]))

    async def KBT_Account(self, user_id):
        acc_info = f'<b>Мой аккаунт</b> \n\n\U0001F518 <b>Имя: </b>{await db.get_user_name(user_id)} ' \
                   f'\n\n\U0001F518<b>Баланс: </b>{int(await db.get_user_balance(user_id))}₽ ' \
                   f'\n\n\U0001F518<b>Дата регистрации: </b>{str(await db.get_user_date(user_id))[:10]}'
        return acc_info, types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="\U0001F4B5 Пополнить", callback_data=BalanceManageCallback(action="choose_way", operation="topup", from_where="main").pack()),
                types.InlineKeyboardButton(text="\U0001F4B8 Вывести", callback_data=BalanceManageCallback(action="choose_way", operation="withd", from_where="main").pack())
            ],
            [types.InlineKeyboardButton(text="\U0001F4D6 Операции", callback_data="story_topup_0000001_")],
            [types.InlineKeyboardButton(text="\U0001F3B2 История игр", callback_data="story_games_0000001_")]
        ])

    async def KBT_Bpmanag(self, user_id):
        a_name = {
            conf.junior_lvl: "Junior \U0001F6BC",
            conf.middle_lvl: "Middle \U0001F476",
            conf.master_lvl: "Master \U0001F464",
            conf.superuser_lvl: "Superuser \U0001F480"
        }.get(await db.adm_lvl_check(user_id), "Ошибка. Обратитесь к главному администратору \U000026A0")
        text = f"<b>\U00002B55 Welcome to BPManage\n\nВаш ID - {user_id}\nУровень доступа - {await db.adm_lvl_check(user_id)} / {a_name}</b>"
        buttons = [
            [
                types.InlineKeyboardButton(text="Транзакции",
                                           callback_data=AdminManageCallback(action="choose_type").pack()),
                types.InlineKeyboardButton(text='Пользователи',
                                           callback_data=AdminManageCallback(action="choose_user").pack())
            ]
        ]
        if await db.adm_lvl_check(user_id) == conf.superuser_lvl:
            buttons.append([
                types.InlineKeyboardButton(text='Администраторы',
                                        callback_data=AdminManageCallback(action="admin_list").pack())])
        return text, types.InlineKeyboardMarkup(inline_keyboard=buttons)


    async def BT_Close(self):
        return types.InlineKeyboardButton(text='\U0000274C Закрыть', callback_data='delete_msg')

    async def BT_Support(self):
        return types.InlineKeyboardButton(text='Связаться с поддержкой', url="https://t.me/OrAndOn")

    async def BT_Lk(self, emoji="\U0001F464"):
        return types.InlineKeyboardButton(text=f'{emoji} Личный кабинет', callback_data='back_to_acc')

    async def BT_AdmLk(self, emoji="\U0001F464"):
        return types.InlineKeyboardButton(text=f'{emoji} В главное меню', callback_data=AdminManageCallback(action="open_main").pack())
