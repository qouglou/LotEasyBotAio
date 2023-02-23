import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import conf
import random
from texts import TextsTg as t
from db import BotDB as db
import games as g

bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot)


db = db('lotEasy.db')


class ButtonsTg:

    async def save_msg(self, msg):
        await db.message_saver(msg.message_id, msg.chat.id, str(msg.text))

    async def ButtonRulesAccept(self, user_id, newbie):
        if newbie:
            text_send = t.m_hello_new
        else:
            text_send = t.m_no_rules
        await bot.send_message(user_id, text_send, parse_mode="Markdown",
                               reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
                                   "\U00002705 Принять правила", "\U0001F4D5 Правила"))

    async def ButtonBan(self, user_id):
        await bot.send_message(user_id, t.m_baned, parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup().add(
            await self.button_support()))

    async def KB_Start(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   types.KeyboardButton("\U0001F680 Начать пользование"))

    async def ButtonNotNew(self, user_id):
        await bot.send_message(user_id, t.m_hello_old,
                               reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(
                                   types.KeyboardButton("\U00002139 Меню")))

    async def KB_Menu(self):
        return types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
            "\U0001F464 Личный кабинет", "\U0001F3AE Игры", "\U00002139 Справка")

    async def KBT_GameBet(self, game):
        if game in ("\U0001F451 Королевская битва", "king"):
            game = "king"
            sh_t = t.m_bet_king
        elif game in ("\U0001F3B2 Русская рулетка", "russ"):
            game = "russ"
            sh_t = t.m_bet_russ
        elif game in ("\U0001F93A Дуэль", "duel"):
            game = "duel"
            sh_t = t.m_bet_duel
        elif game in ("\U0001F3B3 Боулинг", "bowl"):
            game = "bowl"
            sh_t = t.m_bet_bowl
        elif game in ("\U0001F3B2 Бросить кубик", "cube"):
            game = "cube"
            sh_t = t.m_bet_cube
        elif game in ("\U0001F3B0 Крутить рулетку", "slot"):
            game = "slot"
            sh_t = t.m_bet_slot

        async def button_bet(emoji, bet):
            button = types.InlineKeyboardButton(f"{emoji} {bet} ₽", callback_data=f"bet_{game}_{format(bet, '06')}")
            return button
        b_50 = await button_bet("\U0001F4B4", 50)
        b_100 = await button_bet("\U0001F4B5", 100)
        b_500 = await button_bet("\U0001F4B6", 500)
        b_1000 = await button_bet("\U0001F4B0", 1000)
        keyboard = types.InlineKeyboardMarkup(2).add(b_50, b_100, b_500, b_1000)
        if game in ("bowl", "cube", "slot"):
            keyboard.row(types.InlineKeyboardButton("\U0001F4DD Другая сумма", callback_data=f"{game}_bet_other_sum"))
        keyboard.row(types.InlineKeyboardButton('\U00002753 Справка', callback_data=f"que_{game}"))
        return sh_t, keyboard
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

    async def ButtonBetCheck(self, call, user_id=0, game="", sum=0):
        keyboard = types.InlineKeyboardMarkup()
        if call is not 0:
            user_id = call.from_user.id
            game = call.data[4:8]
            sum = int(call.data[9:15].lstrip("0"))
        if game == "king":
            gline = "Королевская битва\U0001F451"
        elif game == "russ":
            gline = "Русская рулетка\U0001F3B2"
        elif game == "duel":
            gline = "Дуэль\U0001F93A"
        elif game == "bowl":
            gline = "Боулинг\U0001F3B3"
        elif game == "cube":
            gline = "Кубик\U0001F3B2"
        elif game == "slot":
            gline = "Рулетка\U0001F3B0"
        if sum <= int(await db.get_user_balance(user_id)):
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
        elif call == 0:
            await bot.send_message(user_id, check_txt, reply_markup=keyboard, parse_mode="Markdown")

    async def ButtonSupport(self, user_id, id_pay, way_topup, msg_id):
        keyboard = types.InlineKeyboardMarkup().add(await self.button_support())
        look = t.m_look_topup
        await bot.edit_message_text(look, user_id, msg_id, parse_mode="Markdown")
        id_pay = id_pay.lstrip(" ")
        N = 5
        while N != 1:
            await asyncio.sleep(1)
            look += "\U000026AA"
            if await db.get_topup_accured(id_pay) == 0:
                await bot.edit_message_text(look, user_id, msg_id, parse_mode="Markdown")
                N -= 1
            elif await db.get_topup_accured(id_pay) == 1:
                break
        if await db.get_topup_accured(id_pay) == 0:
            if way_topup == "bank":
                line_req = "Карта - *1234...*"
            elif way_topup == "qiwi":
                line_req = "QIWI кошелек - *+79...*"
            no_topup = (f"\U0000274C *Перевод не найден*"
                        f"\n\nПроверьте правильность реквизитов и комментария к переводу:\n"
                        f"\n{line_req}\nКомментарий - *№{id_pay}*")
            keyboard.add(types.InlineKeyboardButton('\U0000267B Проверить заново',
                                                        callback_data=f"recheck_topup_{way_topup}_{str(format(id_pay, '7'))}"))
            await bot.edit_message_text(no_topup, user_id, msg_id, reply_markup=keyboard, parse_mode="Markdown")
        elif await db.get_topup_accured(id_pay) == 1:
            await self.ButtonTopupCheck(user_id, way_topup, id_pay, msg_id)

    async def ButtonTopupAlreadyDone(self, user_id):
        await bot.send_message(user_id, t.m_topup_already_done,
                               reply_markup=types.InlineKeyboardMarkup().add(
                                   await self.button_close()), parse_mode="Markdown")

    async def ButtonTopupCheck(self, user_id, way_topup, id_pay, msg_id):
        if await db.get_topup_accured(id_pay) == 0:
            await self.ButtonSupport(user_id, id_pay, way_topup, msg_id)
        elif (await db.get_topup_accured(id_pay) == 1) & (
                await db.get_topup_done(id_pay) == 0):
            await db.topup_balance(user_id, await db.get_topup_sum(id_pay))
            await db.set_topup_done(id_pay)
            m_success_topup = (f"\U00002705 *Транзакция успешно выполнена!*"
                               f"\n\n*Ваш баланс:*\n{int(await db.get_user_balance(user_id))}₽")
            await bot.edit_message_text(m_success_topup, user_id, msg_id,
                                        reply_markup=types.InlineKeyboardMarkup().add(
                                            types.InlineKeyboardButton(await self.button_lk(msg_id))),
                                        parse_mode="Markdown")
        elif await db.get_topup_done(id_pay) == 1:
            await bot.delete_message(user_id, msg_id)
            await self.ButtonTopupAlreadyDone(user_id)

    async def ButtonAccount(self, user_id):
        keyboard = types.InlineKeyboardMarkup(2)
        acc_info = f'*Мой аккаунт* \n\n\U0001F518 *Имя: *{await db.get_user_name(user_id)} ' \
                   f'\n\n\U0001F518*Баланс: *{int(await db.get_user_balance(user_id))}₽ ' \
                   f'\n\n\U0001F518*Дата регистрации: *{str(await db.get_user_date(user_id))[:10]}'
        keyboard.add(types.InlineKeyboardButton('\U0001F4B5 Пополнить', callback_data='topup_balance_main_'),
                     types.InlineKeyboardButton("\U0001F4B8 Вывести", callback_data='withd_balance_main_'))
        keyboard.row(types.InlineKeyboardButton("\U0001F4D6 Операции", callback_data='story_topup_0_'))
        keyboard.row(types.InlineKeyboardButton("\U0001F3B2 История игр", callback_data='story_games_0_'))
        return acc_info, keyboard

    async def GameOffline(self, user_id, game, sum, msg_id):
        await bot.delete_message(user_id, msg_id)
        await db.withdraw_balance(user_id, sum)
        sleep = 4
        if game == "bowl":
            msg = await bot.send_dice(user_id, emoji="\U0001F3B3")
        elif game == "cube":
            msg = await bot.send_dice(user_id, emoji="\U0001F3B2")
        elif game == "slot":
            sleep = 2
            msg = await bot.send_dice(user_id, emoji="\U0001F3B0")
        coef, text = await g.get_offline_values(game, msg.dice.value)
        if coef > 0:
            text += f"Ваш выигрыш составил *{format(float(sum)*coef, '.0f')}₽*!\n\nСыграйте еще!"
            await db.topup_balance(user_id, float(sum)*coef)
        await asyncio.sleep(sleep)
        await bot.send_message(user_id, text, reply_markup=types.InlineKeyboardMarkup(1).add(
            types.InlineKeyboardButton("\U0000267B Сыграть еще раз!", callback_data=f"create_bet_{game}_{sum}"),
            await self.button_lk()), parse_mode="Markdown")

    async def GameOnline(self, user_id, game, sum, msg_id):
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
        while cur_user <= max_num_user:
            free_room = await db.game_check_free(game, cur_user, user_id, sum)
            if free_room is not None:
                break
            cur_user += 1
        if free_room is None:
            await db.game_create(game, user_id, sum)
            num_user = 1
        elif free_room is not None:
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
        create_t = (f"*Вы успешно присоединились к игре*"
                    f"\nКомната - *{id_room}*\nВаш номер - *№{num_user}*"
                    f"\n\n*{gline}*\n\U0001F4B0*{sum}₽*{num_enemys}")
        edited_t = create_t
        await bot.edit_message_text(create_t, user_id, msg_id, parse_mode="Markdown")
        N = 6
        while N != 0:
            await asyncio.sleep(1)
            if await db.game_check_full(game, id_room):
                break
            edited_t += "\U000026AA"
            await bot.edit_message_text(edited_t, user_id, msg_id, parse_mode="Markdown")
            N -= 1
            if N == 1:
                N = 6
                edited_t = create_t
        if game == "duel":
            enemy_found = "*\U00002705 Противник найден!*\n\nНачинаем игру..."
        else:
            enemy_found = "*\U00002705 Противники найдены!*\n\nНачинаем игру..."
        await bot.edit_message_text(enemy_found, user_id, msg_id, parse_mode="Markdown")
        await asyncio.sleep(3)
        msg = await bot.edit_message_text(f"{gline[:1]}Игра началась\nВаше число - *{num_user}*", user_id, msg_id, parse_mode="Markdown")
        await asyncio.sleep(2)
        if await db.win_num_check(game, id_room) == 0:
            await db.win_num_in(game, random.randint(1, max_num_user), id_room)
        await bot.delete_message(user_id, msg.message_id)
        if await db.win_num_check(game, id_room) == 1:
            sticker = "CAACAgEAAxkBAAJKXmP1-D61tx35vn4SJgdiRRxGBxn3AAI8CAAC43gEAAHaKiq0NcyVRi4E"
        elif await db.win_num_check(game, id_room) == 2:
            sticker = "CAACAgEAAxkBAAJKYGP1-RTUHflK7hudhgMyGsTGa3jgAAI9CAAC43gEAAFY6MYzUmo1jC4E"
        elif await db.win_num_check(game, id_room) == 3:
            sticker = "CAACAgEAAxkBAAJKnGP1-6gv9_SN3Aq_U3-fdF8aq3dbAAI-CAAC43gEAAHSR_gvg54YrS4E"
        elif await db.win_num_check(game, id_room) == 4:
            sticker = "CAACAgEAAxkBAAJKnmP1-7O2uYRtPNL51-KjiLHqBxBAAAI_CAAC43gEAAHP2s_5QyNoey4E"
        elif await db.win_num_check(game, id_room) == 5:
            sticker = "CAACAgEAAxkBAAJKoGP1-71SLKKzmLk_RXHrstmowCzdAAJACAAC43gEAAG79fTbfrFmui4E"
        elif await db.win_num_check(game, id_room) == 6:
            sticker ="CAACAgEAAxkBAAJKomP1-8Rz_wl2zODmzcgKUCeFGXtxAAJBCAAC43gEAAGJk5R3VlyCEy4E"
        msg = await bot.send_sticker(user_id, sticker)
        await asyncio.sleep(3.5)
        await bot.delete_message(user_id, msg.message_id)
        if num_user == await db.win_num_check(game, id_room):
            line = f"\U0001F389 *Вы победили!*\n*Выпало число {await db.win_num_check(game, id_room)}*\n\nВаш выигрыш - *{int(sum) * 2}₽*\nПроверьте свою удачу еще раз!\n"
            await db.topup_balance(user_id, int(sum) * 2)
            await db.warned_winner(game, id_room)
        elif num_user != await db.win_num_check(game, id_room):
            line = f"\U0001F383 *Вы проиграли*\n*Выпало число {await db.win_num_check(game, id_room)}*\n\nПроверьте свою удачу еще раз!\n"
        await bot.send_message(user_id, line, parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup(1).add(
            types.InlineKeyboardButton('\U0000267B Попробовать еще раз',
                                               callback_data=f"bet_{game}_{sum}"), await self.button_lk()))

    async def bpmanag_no(self, user_id):
        await bot.send_message(user_id, t.m_manag_no, reply_markup=types.InlineKeyboardMarkup().add(
            await self.button_close()), parse_mode="Markdown")

    async def not_ehough_access(self, adm_id, need_lvl, msg_id=False):
        keyboard = types.InlineKeyboardMarkup().add(await self.button_adm_lk())
        if msg_id:
            await bot.edit_message_text(f"*Недостаточно прав. \n\nНеобходимо иметь уровень {need_lvl} и выше.*",
                                          adm_id, msg_id, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await bot.send_message(adm_id, f"*Недостаточно прав.\n\nНеобходимо иметь уровень {need_lvl} и выше.*",
                reply_markup=keyboard, parse_mode="Markdown")

    async def bpmanag_main(self, user_id):
        keyboard = types.InlineKeyboardMarkup(2).add(types.InlineKeyboardButton("Транзакции", callback_data=f"control_transact"),
                                                     types.InlineKeyboardButton('Пользователи', callback_data=f"control_users"),
                                                     types.InlineKeyboardButton('Админы', callback_data=f"control_admin"))
        if await db.adm_lvl_check(user_id) == conf.junior_lvl:
            a_name = "Junior \U0001F6BC"
        elif await db.adm_lvl_check(user_id) == conf.middle_lvl:
            a_name = "Middle \U0001F476"
        elif await db.adm_lvl_check(user_id) == conf.master_lvl:
            a_name = "Master \U0001F464"
        elif await db.adm_lvl_check(user_id) == conf.superuser_lvl:
            a_name = "Superuser \U0001F480"
        else:
            a_name = "Ошибка. Обратитесь к главному администратору \U000026A0"
        text = f"*{t.m_manag_welcome}\n\nВаш ID - {user_id}\nУровень доступа - {await db.adm_lvl_check(user_id)} / {a_name}*"
        return text, keyboard

    async def bpmanag_no_valid(self, user_id, ex_adm, msg_id=0):
        keyboard = types.InlineKeyboardMarkup().add(await self.button_support())
        if ex_adm:
            await bot.edit_message_text(t.m_no_valid_adm, user_id, msg_id, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await bot.send_message(user_id, t.m_no_valid_adm, reply_markup=keyboard, parse_mode="Markdown")

    async def button_close(self):
        return types.InlineKeyboardButton('\U0000274C Закрыть', callback_data='delete_msg')

    async def button_support(self):
        return types.InlineKeyboardButton('Связаться с поддержкой', url="https://t.me/OrAndOn")

    async def button_lk(self, emoji="\U0001F464"):
        return types.InlineKeyboardButton(f'{emoji} Личный кабинет', callback_data='back_to_acc')

    async def button_adm_lk(self, emoji="\U0001F464"):
        return types.InlineKeyboardButton(f'{emoji} В главное меню', callback_data="main_bpmanag")
