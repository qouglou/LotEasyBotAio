from configs import conf


class TextsTg:

    m_main_info = ("\U0001F3B0 В данном боте вы можете проверить свою удачу.\n"
                   "Для старта игры необходимо выбрать игру и ставку.\n\n"
                    f"Если вы выбрали <b>онлайн</b> игру, то в зависимости от выбора вы попадаете в комнату, где помимо вас находится еще от 1 до {conf.max_users_king-1} игроков. "
                    "Из всех игроков побеждает лишь один.\n"
                   "<b>Выигравший забирает ставки остальных.</b>\n\n"
                   "В <b>быстрой</b> игре в зависимости от выбранной игры выпадает случайное число которое соответствует "
                   "коэффициенту от 0 до 10, на которое умножается ваша ставка.\n\n"
                   "Подробнее про каждую игру вы можете почитать при нажатии на нее в пункте 'Игры'.")

    m_where10 = '\U0001F4CC Содержание и разработка площадки требует денежных средств, из за чего мы вынуждены брать комиссию с каждого вывода средств.\n' \
                    '<b>Комиссия площадки - 5%.\n\n' \
                'Указанный выше текст является лишь возможным вариантом реализации. Данный бот не совершает финансовые операции</b>';

    m_why_rand = ("\U0001F3B2 Выбор чисел для <b>онлайн</b> игр происходит автоматически при помощи генератора псевдослучайных чисел Python модулем random.\n\n"
                  "Для <b>быстрых</b> игр при генерации выпадения числа в смайлике используются сервера Telegram.\n"
                    "\nБольше информации здесь - \n"
                  "https://docs.python.org/3/library/random.html\n"
                  "https://core.telegram.org/api/dice")

    m_question_duel = (f"\U0001F93A В режиме Дуэль вы соперничаете с {conf.max_users_duel-1} противником. Шанс победить - {round((1/conf.max_users_duel)*100)}%.\n\n"
                       "<b>Побеждаете - забираете его ставку.</b>")

    m_question_russ = (f'\U0001F3B2 В режиме Русская рулетка вы соперничаете с {conf.max_users_russ-1} противниками. Шанс победить - {round((1/conf.max_users_russ)*100)}%.\n\n' 
                       f"<b>Побеждаете - забираете ставки {conf.max_users_russ-1} участников.</b>")

    m_question_king = (f'\U0001F451 В режиме Королевская битва вы соперничаете с {conf.max_users_king-1} противниками.\n\n' 
                       "<b>Побеждаете - забираете ставки всех участников.</b>")

    m_question_bowl = (f"\U0001F3B3 Правила просты \n\n"
                       f"Выбиваете <b>страйк</b> - делаете <b>х{conf.bowl_strike}</b>.\n"
                       f"Остается 1 кегля - <b>х{conf.bowl_hit_5}</b>\n"
                       f"Оставшиеся 2 кегли дадут <b>х{conf.bowl_hit_4}</b>\n"
                       f"Осталось 3 кегли - <b>x{conf.bowl_hit_3}</b>\n\n"
                       f"Сбили меньше - увы, ставка не сыграла.")

    m_question_cube = ("\U0001F3B2 Классика всех игр \n\n"
                       "В зависимости от выпаших очков ваша ставка умножается на коэффициент:\n\n"
                       f"<b>6</b> очков - <b>х{conf.dice_6}</b>\n"
                       f"<b>5</b> - <b>x{conf.dice_5}</b>\n"
                       f"<b>4</b> - <b>x{conf.dice_4}</b>\n"
                       f"<b>3</b> - <b>x{conf.dice_3}</b>\n\n"
                       f"Меньше - увы, ставка не сыграла")

    m_question_slot = ("\U0001F3B0 Старый добрый однорукий бандит\n\n"
                       f"Выпало <b>777</b> - словили <b>джекпот</b>! Ваша ставка делает <b>х{conf.slot_jackpot}</b>!\n"
                       f"Три \U0001F347, \U0001F34B или <b>BAR</b> - коэффициент <b>{conf.slot_other_3}</b>\n"
                       f"Любые <b>две 7</b> - Ставка умножается на <b>х{conf.slot_7_2}!</b>\n"
                       f"<b>Одна 7</b> и <b>два</b> \U0001F347, \U0001F34B или <b>BAR</b> - коэффициент <b>х{conf.slot_7_1}</b>\n"
                       f"Даже если все <b>3 разные</b> - кэшбек с коэффициентом <b>x{conf.slot_diff}</b>!\n\n"
                       f"В остальных случаях - увы, ставка не сыграла")

    m_rules = ("\U0001F4CB Использование бота подразумевает согласие с настоящими правилами:\n\n"
               "1. Данный телеграм бот является лишь демонстрацией возможной реализации игрового бота.\n\n"
               "2. Данный бот не является азартной игрой, не принимает платежи и не выводит средства.\n\n"
               "3. Создатель бота не несет ответственности за последствия использования бота.")

    m_enter_requisites_bank = ("<b>Введите номер карты:</b>\n\n"
                               "Формат номера карты - 16 цифр без пробелов и других разделяющих знаков\n"
                               "Например - <i>4617006599722675</i>")

    m_enter_requisites_qiwi = ("<b>Введите номер телефона:</b>\n\n"
                               "Формат номера телефона - 11 цифр без пробелов и других разделяющих знаков с кодом страны в начале (без + в начале)\n"
                               "Например - <i>79999224601</i>")

    m_topup_create_1 = ("\U0000267B<b>Ваша транзакция зарегистрирована!</b>\n\n"
                            "\U0001F4B8 Для ее выполнения совершите перевод")

    m_topup_create_2 = ("\n\n<b>После</b> выполнения перевода нажмите кнопку ниже\n\n"
                        "<b>Указаный выше текст является лишь демонстрацией возможного варианта реализации бота!\n"
                        "Бот не принимает переводы и не совершает финансовые операции!</b>")

    dct_games_que = {
        "duel": m_question_duel,
        "king": m_question_king,
        "russ": m_question_russ,
        "bowl": m_question_bowl,
        "cube": m_question_cube,
        "slot": m_question_slot
        }

    dct_enter_req = {
        "bank": m_enter_requisites_bank,
        "qiwi": m_enter_requisites_qiwi
    }

    dct_type_way = {
        "topup": "<b>Выберите способ пополнения</b>",
        "withd": "<b>Выберите способ вывода средств</b>"
    }

    dct_que_answ = {
        "\U0001F4AC Комиссия": m_where10,
        "\U0001F4AC Алгоритмы": m_why_rand,
        "\U0001F4AC Правила": m_rules
    }

