import asyncio

from aiogram import Bot, types, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import conf
import random
from db import BotDB as db
from buttons import ButtonsTg as b
from callback_factory import BalanceManageCallback

bot = Bot(token=conf.TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

db = db('lotEasy.db')


class Games:

    async def get_offline_values(self, game, dice_value):
        coef = 0
        txt = "<b>К сожалению, вы ничего не выиграли\n\nПопробуйте еще раз!</b>"
        if game == "bowl":
            if dice_value == 6:
                coef = conf.bowl_strike
                txt = "<b>Страйк! \U0001F389\U0001F911\nПоздравляем!</b>\n\n"
            elif dice_value == 5:
                coef = conf.bowl_hit_5
                txt = "<b>5 сбитых - отличный результат!</b>\n\n"
            elif dice_value == 4:
                coef = conf.bowl_hit_4
                txt = "<b>4 сбитых - неплохой результат</b>\n\n"
            elif dice_value == 3:
                coef = conf.bowl_hit_3
                txt = "<b>Половина сбита - ни туда, ни сюда</b>\n\n"
        elif game == "cube":
            if dice_value == 6:
                coef = conf.dice_6
                txt = "<b>6 очков! Отлично! \U0001F389\U0001F911\nПоздравляем!</b>\n\n"
            elif dice_value == 5:
                coef = conf.dice_5
                txt = "<b>5 очков - отличный результат!</b>\n\n"
            elif dice_value == 4:
                coef = conf.dice_4
                txt = "<b>На кубике 4 - неплохой результат</b>\n\n"
            elif dice_value == 3:
                coef = conf.bowl_hit_3
                txt = "<b>3 точки - ни туда, ни сюда</b>\n\n"
        elif game == "slot":
            if dice_value == 64:
                coef = conf.slot_jackpot
                txt = "<b>Джекпот! \U0001F389\U0001F911\nУдача явно на вашей стороне!</b>\n\n"
            elif dice_value in (1, 22, 43):
                coef = conf.slot_other_3
                txt = "<b>3 в ряд! Вот это удача! \U0001F389\U0001F911\nПоздравляем!</b>\n\n"
            elif dice_value in (16, 32, 48, 52, 56, 60, 61, 62, 63):
                coef = conf.slot_7_2
                txt = "<b>Две семерки - тоже победа! \U0001F389\nПоздравляем!</b>\n\n"
            elif dice_value in (4, 13, 24, 30, 44, 47, 49, 54, 59):
                coef = conf.slot_7_1
                txt = "<b>Одна семерка и два в ряд - неплохо! \U0001F389\nПоздравляем!</b>\n\n"
            elif dice_value in (
            7, 8, 10, 12, 14, 15, 19, 20, 25, 28, 29, 31, 34, 36, 37, 40, 45, 46, 50, 51, 53, 55, 57, 58):
                coef = conf.slot_diff
                txt = "<b>Выбить все разное - тоже надо постараться!</b>\n\n"
        return coef, txt

    async def games_offline(self, user_id, game, sum, msg_id):
        await bot.delete_message(user_id, msg_id)
        try:
            room_id = (await db.check_free_room(game, sum))[0]
        except:
            room_id = await db.check_free_room(game, sum)
            while room_id is None:
                await db.create_room_game(game, sum)
                room_id = (await db.check_free_room(game, sum))[0]
        await db.add_user_to_game_room(room_id, user_id, 0, game, await db.get_user_balance(user_id))
        await db.set_room_full(room_id)
        await db.set_withdraw_balance(user_id, sum)
        sleep = 4
        if game == "bowl":
            msg = await bot.send_dice(user_id, emoji="\U0001F3B3")
        elif game == "cube":
            msg = await bot.send_dice(user_id, emoji="\U0001F3B2")
        elif game == "slot":
            sleep = 2
            msg = await bot.send_dice(user_id, emoji="\U0001F3B0")
        coef, text = await self.get_offline_values(game, msg.dice.value)
        if await db.win_num_check(room_id) == 0:
            await db.set_topup_balance(user_id, float(sum) * coef)
            await db.update_win_num_in(int(msg.dice.value), room_id)
            await db.update_win_sum_in(room_id, user_id, float(sum) * coef)
            await db.set_game_end(room_id)
            if coef > 0:
                text += f"Ваш выигрыш составил <b>{format(float(sum) * coef, '.0f')}₽</b>!\n\nСыграйте еще!"
            await asyncio.sleep(sleep)
            await bot.send_message(user_id, text, reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="\U0000267B Сыграть еще раз!",
                                            callback_data=BalanceManageCallback(action="create_bet", game=game,
                                                                                sum=sum).pack())],
                [await b().BT_Lk()]
            ]))
            await db.warned_winner(room_id, user_id)
        else:
            await bot.send_message(user_id, "<b>Игра уже была сыграна\n\nЕсли вы не получили уведомления о результате,"
                                            "а ваш баланс не изменился, подождите 5 минут. \nЕсли в течении данного времени "
                                            "вы не получите уведомления, обратитесь в поддержку.</b>",
                                   reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                       [await b().BT_Support()],
                                       [await b().BT_Lk()]
                                   ]))

    async def games_online(self, user_id, game, sum, msg_id):
        if game == "king":
            gline = "\U0001F451 Королевская битва"
            max_num_user = conf.max_users_king
        elif game == "russ":
            gline = "\U0001F3B2 Русская рулетка"
            max_num_user = conf.max_users_russ
        elif game == "duel":
            gline = "\U0001F93A Дуэль"
            max_num_user = conf.max_users_duel
        try:
            room_id = (await db.check_free_room(game, sum))[0]
            if await db.check_user_second_game(room_id, user_id) == 1:
                raise
        except:
            room_id = None
            while room_id is None:
                await db.create_room_game(game, sum)
                room_id = (await db.check_free_room(game, sum, "DESC"))[0]
        user_num = await db.get_user_num(room_id) + 1
        await db.add_user_to_game_room(room_id, user_id, user_num, game, await db.get_user_balance(user_id))
        await db.set_withdraw_balance(user_id, sum)
        if user_num == max_num_user:
            await db.set_room_full(room_id)
            await db.update_win_num_in(random.randint(1, max_num_user), room_id)
        if game == "duel":
            num_enemys = "\n\nОжидание противника\n"
        else:
            num_enemys = "\n\nОжидание противников\n"
        create_t = (f"<b>Вы успешно присоединились к игре</b>"
                    f"\nКомната - <b>{room_id}</b>\nВаш номер - <b>№{user_num}</b>"
                    f"\n\n<b>{gline}</b>\n\U0001F4B0<b>{sum}₽</b>{num_enemys}")
        edited_t = create_t
        await bot.edit_message_text(create_t, user_id, msg_id)
        N = 6
        while N != 0:
            await asyncio.sleep(1)
            if await db.check_game_full(room_id):
                break
            edited_t += "\U000026AA"
            await bot.edit_message_text(edited_t, user_id, msg_id)
            N -= 1
            if N == 1:
                N = 6
                edited_t = create_t
        if game == "duel":
            enemy_found = "<b>\U00002705 Противник найден!</b>\n\nНачинаем игру..."
        else:
            enemy_found = "<b>\U00002705 Противники найдены!</b>\n\nНачинаем игру..."
        await bot.edit_message_text(enemy_found, user_id, msg_id)
        await asyncio.sleep(3)
        msg = await bot.edit_message_text(f"{gline[:1]}Игра началась\nВаше число - <b>{user_num}</b>", user_id, msg_id)
        await asyncio.sleep(2)
        await bot.delete_message(user_id, msg.message_id)
        sticker = {
            1: "CAACAgEAAxkBAAJKXmP1-D61tx35vn4SJgdiRRxGBxn3AAI8CAAC43gEAAHaKiq0NcyVRi4E",
            2: "CAACAgEAAxkBAAJKYGP1-RTUHflK7hudhgMyGsTGa3jgAAI9CAAC43gEAAFY6MYzUmo1jC4E",
            3: "CAACAgEAAxkBAAJKnGP1-6gv9_SN3Aq_U3-fdF8aq3dbAAI-CAAC43gEAAHSR_gvg54YrS4E",
            4: "CAACAgEAAxkBAAJKnmP1-7O2uYRtPNL51-KjiLHqBxBAAAI_CAAC43gEAAHP2s_5QyNoey4E",
            5: "CAACAgEAAxkBAAJKoGP1-71SLKKzmLk_RXHrstmowCzdAAJACAAC43gEAAG79fTbfrFmui4E",
            6: "CAACAgEAAxkBAAJKomP1-8Rz_wl2zODmzcgKUCeFGXtxAAJBCAAC43gEAAGJk5R3VlyCEy4E"
        }[await db.win_num_check(room_id)]
        msg = await bot.send_sticker(user_id, sticker)
        await asyncio.sleep(3.5)
        await bot.delete_message(user_id, msg.message_id)
        if user_num == await db.win_num_check(room_id):
            line = f"\U0001F389 <b>Вы победили!</b>\n<b>Выпало число {await db.win_num_check(room_id)}</b>\n\nВаш выигрыш - <b>{int(sum) * 2}₽</b>\nПроверьте свою удачу еще раз!\n"
            await db.set_topup_balance(user_id, int(sum) * 2)
            await db.update_win_sum_in(room_id, user_id, int(sum) * 2)
        elif user_num != await db.win_num_check(room_id):
            line = f"\U0001F383 <b>Вы проиграли</b>\n<b>Выпало число {await db.win_num_check(room_id)}</b>\n\nПроверьте свою удачу еще раз!\n"
            await db.update_win_sum_in(room_id, user_id, 0)
        if not await db.check_game_end(room_id):
            await db.set_game_end(room_id)
        await bot.send_message(user_id, line,
                               reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                                   [types.InlineKeyboardButton(text='\U0000267B Попробовать еще раз',
                                                               callback_data=BalanceManageCallback(action="create_bet", game=game, sum=sum).pack())],
                                   [await b().BT_Lk()]
                               ]))
        await db.warned_winner(room_id, user_id)
