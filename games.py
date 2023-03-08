import asyncio

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
import conf
import random
from db import BotDB as db
from buttons import ButtonsTg as b

bot = Bot(token=conf.TOKEN)
dp = Dispatcher(bot)


db = db('lotEasy.db')


class Games:

    async def get_offline_values(self, game, dice_value):
        coef = 0
        txt = "*К сожалению, вы ничего не выиграли\n\nПопробуйте еще раз!*"
        if game == "bowl":
            if dice_value == 6:
                coef = conf.bowl_strike
                txt = "*Страйк! \U0001F389\U0001F911\nПоздравляем!*\n\n"
            elif dice_value == 5:
                coef = conf.bowl_hit_5
                txt = "*5 сбитых - отличный результат!*\n\n"
            elif dice_value == 4:
                coef = conf.bowl_hit_4
                txt = "*4 сбитых - неплохой результат*\n\n"
            elif dice_value == 3:
                coef = conf.bowl_hit_3
                txt = "*Половина сбита - ни туда, ни сюда*\n\n"
        elif game == "cube":
            if dice_value == 6:
                coef = conf.dice_6
                txt = "*6 очков! Отлично! \U0001F389\U0001F911\nПоздравляем!*\n\n"
            elif dice_value == 5:
                coef = conf.dice_5
                txt = "*5 очков - отличный результат!*\n\n"
            elif dice_value == 4:
                coef = conf.dice_4
                txt = "*На кубике 4 - неплохой результат*\n\n"
            elif dice_value == 3:
                coef = conf.bowl_hit_3
                txt = "*3 точки - ни туда, ни сюда*\n\n"
        elif game == "slot":
            if dice_value == 64:
                coef = conf.slot_jackpot
                txt = "*Джекпот! \U0001F389\U0001F911\nУдача явно на вашей стороне!*\n\n"
            elif dice_value in (1, 22, 43):
                coef = conf.slot_other_3
                txt = "*3 в ряд! Вот это удача! \U0001F389\U0001F911\nПоздравляем!*\n\n"
            elif dice_value in (16, 32, 48, 52, 56, 60, 61, 62, 63):
                coef = conf.slot_7_2
                txt = "*Две семерки - тоже победа! \U0001F389\nПоздравляем!*\n\n"
            elif dice_value in (4, 13, 24, 30, 44, 47, 49, 54, 59):
                coef = conf.slot_7_1
                txt = "*Одна семерка и два в ряд - неплохо! \U0001F389\nПоздравляем!*\n\n"
            elif dice_value in (7, 8, 10, 12, 14, 15, 19, 20, 25, 28, 29, 31, 34, 36, 37, 40, 45, 46, 50, 51, 53, 55, 57, 58):
                coef = conf.slot_diff
                txt = "*Выбить все разное - тоже надо постараться!*\n\n"
        return coef, txt

    async def games_offline(self, user_id, game, sum, msg_id):
        await bot.delete_message(user_id, msg_id)
        await db.set_withdraw_balance(user_id, sum)
        await db.add_offline_game(game, user_id, sum)
        sleep = 4
        if game == "bowl":
            msg = await bot.send_dice(user_id, emoji="\U0001F3B3")
        elif game == "cube":
            msg = await bot.send_dice(user_id, emoji="\U0001F3B2")
        elif game == "slot":
            sleep = 2
            msg = await bot.send_dice(user_id, emoji="\U0001F3B0")
        id_room = await db.offline_game_get_id(game, user_id, sum)
        coef, text = await self.get_offline_values(game, msg.dice.value)
        if await db.win_num_check("offl", id_room) == 0:
            await db.set_topup_balance(user_id, float(sum) * coef)
            await db.offline_win_num_in(int(msg.dice.value), id_room)
            if coef > 0:
                text += f"Ваш выигрыш составил *{format(float(sum)*coef, '.0f')}₽*!\n\nСыграйте еще!"
            await asyncio.sleep(sleep)
            await bot.send_message(user_id, text, reply_markup=types.InlineKeyboardMarkup(1).add(
                types.InlineKeyboardButton("\U0000267B Сыграть еще раз!", callback_data=f"create_bet_{game}_{format(sum, '06')}"),
                await b().BT_Lk()), parse_mode="Markdown")
            await db.warned_winner("offl", id_room)
        else:
            await bot.send_message(user_id, "*Игра уже была сыграна\n\nЕсли вы не получили уведомления о результате,"
                                            "а ваш баланс не изменился, подождите 5 минут. \nЕсли в течении данного времени "
                                            "вы не получите уведомления, обратитесь в поддержку.*", reply_markup=types.InlineKeyboardMarkup(1).add(
                await b().BT_Support(), await b().BT_Lk()), parse_mode="Markdown")

    async def games_online(self, user_id, game, sum, msg_id):
        await db.set_withdraw_balance(user_id, sum)
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
            await db.add_online_game(game, user_id, sum)
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
        sticker = {
            1: "CAACAgEAAxkBAAJKXmP1-D61tx35vn4SJgdiRRxGBxn3AAI8CAAC43gEAAHaKiq0NcyVRi4E",
            2: "CAACAgEAAxkBAAJKYGP1-RTUHflK7hudhgMyGsTGa3jgAAI9CAAC43gEAAFY6MYzUmo1jC4E",
            3: "CAACAgEAAxkBAAJKnGP1-6gv9_SN3Aq_U3-fdF8aq3dbAAI-CAAC43gEAAHSR_gvg54YrS4E",
            4: "CAACAgEAAxkBAAJKnmP1-7O2uYRtPNL51-KjiLHqBxBAAAI_CAAC43gEAAHP2s_5QyNoey4E",
            5: "CAACAgEAAxkBAAJKoGP1-71SLKKzmLk_RXHrstmowCzdAAJACAAC43gEAAG79fTbfrFmui4E",
            6: "CAACAgEAAxkBAAJKomP1-8Rz_wl2zODmzcgKUCeFGXtxAAJBCAAC43gEAAGJk5R3VlyCEy4E"
        }[await db.win_num_check(game, id_room)]
        msg = await bot.send_sticker(user_id, sticker)
        await asyncio.sleep(3.5)
        await bot.delete_message(user_id, msg.message_id)
        if num_user == await db.win_num_check(game, id_room):
            line = f"\U0001F389 *Вы победили!*\n*Выпало число {await db.win_num_check(game, id_room)}*\n\nВаш выигрыш - *{int(sum) * 2}₽*\nПроверьте свою удачу еще раз!\n"
            await db.set_topup_balance(user_id, int(sum) * 2)
            await db.warned_winner(game, id_room)
        elif num_user != await db.win_num_check(game, id_room):
            line = f"\U0001F383 *Вы проиграли*\n*Выпало число {await db.win_num_check(game, id_room)}*\n\nПроверьте свою удачу еще раз!\n"
        await bot.send_message(user_id, line, parse_mode="Markdown", reply_markup=types.InlineKeyboardMarkup(1).add(
            types.InlineKeyboardButton('\U0000267B Попробовать еще раз',
                                               callback_data=f"bet_{game}_{sum}"), await b().BT_Lk()))