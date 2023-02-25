from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import conf
from db import BotDB as db

bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot)


db = db('lotEasy.db')


class ButtonsTg:

    async def KB_Start(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   types.KeyboardButton("\U0001F680 Начать пользование"))

    async def KB_Menu(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
            "\U0001F464 Личный кабинет", "\U0001F3AE Игры", "\U00002139 Справка")

    async def KB_Sum(self, type, key, way="", fr=""):
        async def BT_sum(type, key, way, emoji, sum):
            if type == "game":
                button = types.InlineKeyboardButton(f"{emoji} {sum} ₽", callback_data=f"bet_{key}_{format(sum, '06')}")
            elif type == "oper":
                button = types.InlineKeyboardButton(f"{emoji} {sum} ₽",
                                                  callback_data=f"{way}_{key}_sum_{format(sum, '06')}")
            return button
        b_50 = await BT_sum(type, key, way, "\U0001F4B4", 50)
        b_100 = await BT_sum(type, key, way, "\U0001F4B5", 100)
        b_500 = await BT_sum(type, key, way, "\U0001F4B6", 500)
        b_1000 = await BT_sum(type, key, way, "\U0001F4B0", 1000)
        keyboard = types.InlineKeyboardMarkup(2).add(b_50, b_100, b_500, b_1000)
        if type == "game":
            if key in ("bowl", "cube", "slot"):
                keyboard.row(types.InlineKeyboardButton("\U0001F4DD Другая сумма", callback_data=f"{key}_bet_other_sum"))
            keyboard.row(types.InlineKeyboardButton('\U00002753 Справка', callback_data=f"que_{key}"))
        elif type == "oper":
            keyboard.row(types.InlineKeyboardButton('\U0001F4DD Другая сумма',
                                                 callback_data=f"{way}_{key}_other_sum"))
            keyboard.row(types.InlineKeyboardButton('\U00002B05 Назад',
                                                     callback_data=f"{key}_balance_{fr}"))
        return keyboard

    async def KBT_GameBet(self, game):
        if game in ("\U0001F451 Королевская битва", "king"):
            game = "king"
            sh_t = "\U0001F451 Шанс мал, но приз огромен!\nУдачи!\n\n*Выберите сумму:*"
        elif game in ("\U0001F3B2 Русская рулетка", "russ"):
            game = "russ"
            sh_t = "\U0001F3B2 1 на 5, отличный выбор!\nЖелаем вам удачи!\n\n*Выберите сумму:*"
        elif game in ("\U0001F93A Дуэль", "duel"):
            game = "duel"
            sh_t = "\U0001F93A 1 на 1, 50 на 50, шансы удвоить сумму высоки!\nУдачи!\n\n*Выберите сумму:*"
        elif game in ("\U0001F3B3 Боулинг", "bowl"):
            game = "bowl"
            sh_t = "\U0001F3B3 Чтож, сыграем в боулинг!\n\n*Выберите сумму:*"
        elif game in ("\U0001F3B2 Бросить кубик", "cube"):
            game = "cube"
            sh_t = "\U0001F3B2 Старый добрый кубик!\n\n*Выберите сумму:*"
        elif game in ("\U0001F3B0 Крутить рулетку", "slot"):
            game = "slot"
            sh_t = "\U0001F3B0 Жми на рычаг и испытай свою удачу!\n\n*Выберите сумму:*"
        return sh_t, await self.KB_Sum("game", game)

    async def KB_MainGames(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
            "\U0001F680 Быстрая игра", "\U0001F4BB Онлайн", "\U00002B05 В меню")

    async def KB_OnlineGames(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
            "\U0001F93A Дуэль", "\U0001F3B2 Русская рулетка",
            "\U0001F451 Королевская битва", "\U00002B05 Назад")

    async def KB_OfflineGames(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
            "\U0001F3B3 Боулинг", "\U0001F3B2 Бросить кубик",
            "\U0001F3B0 Крутить рулетку", "\U00002B05 Назад")

    async def KB_Info(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
            "\U0001F4AC Комиссия", "\U0001F4AC Алгоритмы", "\U0001F4AC Правила",
            "\U0001F4AC Поддержка", "\U00002B05 В меню")

    async def ButtonTopupCheck(self, user_id, way_topup, id_pay, msg_id):
        if await db.get_topup_accured(id_pay) == 0:
            await bot.edit_message_text("*Транзакция не найдена.*\n\nПроверьте перевод еще раз, либо обратитесь к поддержке",
                                        user_id, msg_id, reply_markup=
                                        types.InlineKeyboardMarkup(1).add(await self.BT_Support(),
                                                                          types.InlineKeyboardButton(
                                                                              '\U0000267B Проверить еще раз',
                                                                              callback_data=f"check_topup_{way_topup}_{format(id_pay, '7')}", parse_mode="Markdown")))
        elif (await db.get_topup_accured(id_pay) == 1) & (
                await db.get_topup_done(id_pay) == 0):
            await db.topup_balance(user_id, await db.get_topup_sum(id_pay))
            await db.set_topup_done(id_pay)
            m_success_topup = (f"\U00002705 *Транзакция успешно выполнена!*"
                               f"\n\n*Ваш баланс:*\n{int(await db.get_user_balance(user_id))}₽")
            await bot.edit_message_text(m_success_topup, user_id, msg_id,
                                        reply_markup=types.InlineKeyboardMarkup().add(
                                            types.InlineKeyboardButton(await self.BT_lk(msg_id))),
                                        parse_mode="Markdown")
        elif await db.get_topup_done(id_pay) == 1:
            await bot.delete_message(user_id, msg_id)
            await bot.send_message(user_id, "*Данная транзакция уже выполнена*",
                                   reply_markup=types.InlineKeyboardMarkup().add(
                                       await self.BT_close()), parse_mode="Markdown")

    async def KBT_Account(self, user_id):
        keyboard = types.InlineKeyboardMarkup(2)
        acc_info = f'*Мой аккаунт* \n\n\U0001F518 *Имя: *{await db.get_user_name(user_id)} ' \
                   f'\n\n\U0001F518*Баланс: *{int(await db.get_user_balance(user_id))}₽ ' \
                   f'\n\n\U0001F518*Дата регистрации: *{str(await db.get_user_date(user_id))[:10]}'
        keyboard.add(types.InlineKeyboardButton('\U0001F4B5 Пополнить', callback_data='topup_balance_main_'),
                     types.InlineKeyboardButton("\U0001F4B8 Вывести", callback_data='withd_balance_main_'))
        keyboard.row(types.InlineKeyboardButton("\U0001F4D6 Операции", callback_data='story_topup_1'))
        keyboard.row(types.InlineKeyboardButton("\U0001F3B2 История игр", callback_data='story_games_1_'))
        return acc_info, keyboard

    async def KBT_Bpmanag(self, user_id):
        keyboard = types.InlineKeyboardMarkup(2).add(types.InlineKeyboardButton("Транзакции", callback_data=f"control_transact"),
                                                     types.InlineKeyboardButton('Пользователи', callback_data=f"control_users"),
                                                     types.InlineKeyboardButton('Админы', callback_data=f"control_admin"))
        a_name = {
            conf.junior_lvl: "Junior \U0001F6BC",
            conf.middle_lvl: "Middle \U0001F476",
            conf.master_lvl: "Master \U0001F464",
            conf.superuser_lvl: "Superuser \U0001F480"
        }.get(await db.adm_lvl_check(user_id), "Ошибка. Обратитесь к главному администратору \U000026A0")
        text = f"*\U00002B55 Welcome to BPManage\n\nВаш ID - {user_id}\nУровень доступа - {await db.adm_lvl_check(user_id)} / {a_name}*"
        return text, keyboard

    async def BT_Close(self):
        return types.InlineKeyboardButton('\U0000274C Закрыть', callback_data='delete_msg')

    async def BT_Support(self):
        return types.InlineKeyboardButton('Связаться с поддержкой', url="https://t.me/OrAndOn")

    async def BT_Lk(self, emoji="\U0001F464"):
        return types.InlineKeyboardButton(f'{emoji} Личный кабинет', callback_data='back_to_acc')

    async def BT_AdmLk(self, emoji="\U0001F464"):
        return types.InlineKeyboardButton(f'{emoji} В главное меню', callback_data="main_bpmanag")
