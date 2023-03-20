import asyncio

from aiogram import Bot, types
from configs import conf
import games
from games import Games as g
from callback_factory import BalanceManageCallback
from templates.buttons import ButtonsTg as b
from db_conn_create import db
from configs.logs_config import logs


class Checkers:

    async def topup_cheker_all(self, bot: Bot):
        logs.warning(f"Topup checker is successfully  started")
        while True:
            logs.warning(f"Lines not done topups - {await db.get_lines_not_done_topup()}")
            M = 0
            while M < int(await db.get_lines_not_done_topup()):
                int_pay, user_id, sum, accrued, done = await db.all_no_topup_checker()
                if accrued and done is False:
                    m_success_topup = (f"\U00002705 <b>Пополнение №{int_pay} успешно выполнено!</b>"
                                       f"\n\n<b>Ваш баланс:</b>\n{int(await db.get_user_balance(user_id))}₽")
                    try:
                        await bot.send_message(user_id, m_success_topup,
                                           reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                               [await b().BT_Lk()]
                                           ]))
                        await db.set_topup_balance(user_id, sum)
                        await db.set_topup_done(int_pay)
                        logs.warning(f"User {user_id} is automatically warned about his success topup №{int_pay}")
                    except:
                        pass
                M += 1
            await asyncio.sleep(conf.ch_topup_timer)

    async def topup_checker_user(self, message: types.Message, id_pay):
        if await db.get_topup_accured(id_pay) == 0:
            text = "<b>Поиск транзакции</b>\n\n"
            N = 5
            while N != 0:
                text += "\U000026AA"
                await message.edit_text(text=text)
                await asyncio.sleep(1)
                N -= 1
            logs.info(f"User {message.chat.id} unsuccessfully tried to find his topup №{id_pay}")
            await message.edit_text(text=f"<b>Транзакция №{id_pay} не найдена.\n\nПроверьте перевод еще раз, либо обратитесь к поддержке</b>",
                                        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                    [await b().BT_Support()],
                    [types.InlineKeyboardButton(text='\U0000267B Проверить еще раз',
                                                  callback_data=BalanceManageCallback(
                                                      action="check_topup",
                                                      id_oper=id_pay,
                                                      id_msg=message.message_id
                                                  ).pack())]
                ]))
        elif (await db.get_topup_accured(id_pay) == 1) & (
                await db.get_topup_done(id_pay) == 0):
            await db.set_topup_balance(message.from_user.id, await db.get_topup_sum(id_pay))
            await db.set_topup_done(id_pay)
            logs.info(f"User {message.chat.id} successfully get his topup №{id_pay}")
            m_success_topup = (f"\U00002705 <b>Транзакция успешно выполнена!</b>"
                               f"\n\n<b>Ваш баланс:</b>\n{int(await db.get_user_balance(message.chat.id))}₽")
            await message.edit_text(text=m_success_topup, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                            [await b().BT_Lk()]
                                        ]))
        elif await db.get_topup_done(id_pay) == 1:
            await message.delete()
            logs.info(f"User {message.chat.id} tried to get his topup №{id_pay} again")
            await message.answer(text="<b>Данная транзакция уже выполнена</b>",
                                   reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                       [await b().BT_Close()]
                                   ]))

    async def data_checker(self, mfu):
        if (await db.get_user_name(mfu.id) != mfu.first_name) or (
                await db.get_user_lastname(mfu.id) != mfu.last_name) or (
                await db.get_user_username(mfu.id) != mfu.username):
            await db.update_data(mfu.first_name, mfu.last_name, mfu.username,
                                 mfu.id)

    async def bet_sum_checker(self, message: types.Message, game, sum, action, msg_id=0):
        buttons = []
        if sum <= int(await db.get_user_balance(message.chat.id)):
            if action == "create_bet":
                if game in ("king", "russ", "duel"):
                    await games.Games().games_online(message, game, sum)
                elif game in ("bowl", "cube", "slot"):
                    await games.Games().games_offline(message, game, sum)
                return
            else:
                gline = {
                    "duel": "Дуэль\U0001F93A",
                    "king": "Королевская битва\U0001F451",
                    "russ": "Русская рулетка\U0001F3B2",
                    "bowl": "Боулинг\U0001F3B3",
                    "cube": "Кубик\U0001F3B2",
                    "slot": "Рулетка\U0001F3B0"
                }[game]
                check_txt = (f"<b>Выбранные параметры:</b>\n\nИгра - <b>{gline}</b>\nСтавка - <b>{sum}₽\U0001F4B0</b>")
                buttons.append([types.InlineKeyboardButton(text='\U00002705 Подтвердить',
                                                    callback_data=BalanceManageCallback(
                                                        action="create_bet",
                                                        game=game,
                                                        sum=sum
                                                    ).pack())])
        elif sum > await db.get_user_balance(message.chat.id):
            check_txt = (f"<b>Недостаточно средств:</b>\n\nБаланс - <b>{int(await db.get_user_balance(message.chat.id))}₽</b>"
                         f"\nСтавка - <b>{sum}₽</b>")
            buttons.append([types.InlineKeyboardButton(text='\U0001F4B5 Пополнить',
                                                       callback_data=BalanceManageCallback(
                                                           action="choose_way",
                                                           from_where=game,
                                                           operation="topup"
                                                       ).pack())])
        buttons.append([types.InlineKeyboardButton(text='\U0000267B Изменить',
                                                   callback_data=BalanceManageCallback(
                                                       action="choose_bet",
                                                       from_where=game
                                                   ).pack())])
        if msg_id != 0:
            await message.edit_text(text=check_txt, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))
        else:
            await message.answer(text=check_txt, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=buttons))

    async def winner_warned_checker(self, bot: Bot):
        logs.warning(f"Checking the notifications of the winners")
        while True:
            count_lines = await db.get_no_warned_player_lines()
            M = 0
            logs.warning(f"Lines not warned winners - {count_lines}")
            while M < count_lines:
                user_id, user_num, id_room, game, bet, win_num, win_sum, time_end = [str(x) for x in await db.get_all_no_warned_checker()]
                g_line = {
                    "duel": "Дуэль",
                    "russ": "Русская рулетка",
                    "king": "Королевская битва",
                    "bowl": "Боулинг",
                    "cube": "Кубик",
                    "slot": "Рулетка"
                }[game]
                if game in ("duel", "russ", "king"):
                    num_players = {
                        "duel": conf.max_users_duel,
                        "russ": conf.max_users_russ,
                        "king": conf.max_users_king
                    }[game]
                    if user_num == win_num:
                        line = f"<b>Уведомление \U000026A0\n\n" \
                               f"Вы победили в игре {g_line} №{id_room}!\n\n" \
                               f"Ваш выигрыш - {int(float(bet)*float(num_players))}₽\n" \
                               f"Испытайте удачу еще раз!</b>"
                        if win_sum == "None":
                            await db.update_win_sum_in(id_room, user_id, float(bet)*float(num_players))
                    else:
                        line = f"<b>Уведомление \U000026A0\n\n" \
                               f"Игра {g_line} №{id_room} была завершена</b>\n\n" \
                               f"К сожалению, вы проиграли!\n" \
                               f"<b>Испытайте удачу еще раз!</b>"
                        if win_sum == "None":
                            await db.update_win_sum_in(id_room, user_id, 0)
                elif game in ("bowl", "cube", "slot"):
                    coef, text = await g().get_offline_values(game, int(win_num))
                    if coef > 0:
                        text += f"Ваш выигрыш составил <b>{format(float(bet) * coef, '.0f')}₽</b>!\n\n" \
                                f"<b>Сыграйте еще раз!</b>"
                        if win_sum == "None":
                            await db.update_win_sum_in(id_room, user_id, float(bet) * coef)
                    else:
                        if win_sum == "None":
                            await db.update_win_sum_in(id_room, user_id, 0)
                    line = f"<b>Уведомление \U000026A0\n\n" \
                           f"Произведен расчет за игру {g_line} №{id_room}\n</b>" \
                           f"{text}"
                key_again = types.InlineKeyboardButton(text="\U0000267B Сыграть еще раз!",
                                            callback_data=BalanceManageCallback(
                                                action="create_bet",
                                                game=game,
                                                sum=bet
                                            ).pack())
                try:
                    await bot.send_message(chat_id=user_id, text=line,
                                       reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                           [key_again],
                                           [await b().BT_Lk()]
                                       ]))
                    await db.warned_winner(id_room, user_id)
                    logs.warning(f"User {user_id} is automatically warned about his game №{id_room}")
                except:
                    pass
            M += 1
            await asyncio.sleep(conf.ch_winner_timer)
