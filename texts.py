class TextsTg:

    m_main_info = ("\U0001F3B0 В данном боте вы можете проверить свою удачу. "
                   "\nДля старта игры необходимо выбрать игру и ставку. "
                    "\n\nЕсли вы выбрали <b>онлайн</b> игру, то в зависимости от выбора вы попадаете в комнату, где помимо вас находится еще от 1 до 99 игроков. "
                    "Из всех игроков побеждает лишь один."
                   "\n<b>Выигравший забирает ставки остальных.</b>"
                   "\n\nВ <b>быстрой</b> игре в зависимости от выбранной игры выпадает случайное число которое соответствует"
                   " коэффициенту от 0 до 10, на которое умножается ваша ставка."
                   "\n"
                    '\nПодробнее про каждую игру вы можете почитать при нажатии на нее в пункте "Игры".')

    m_where10 = '\U0001F4CC Содержание и разработка площадки требует денежных средств, из за чего мы вынуждены брать комиссию с каждой игры. ' \
                    '\n<b>Комиссия площадки - 5%.</b>';

    m_why_rand = ("\U0001F3B2 Выбор чисел для <b>онлайн</b> игр происходит автоматически при помощи генератора случайных чисел random.org."
                  "\n"
                    "Данный сервис генерирует числа на основе атмосферных шумов."
                  "\n\nДля <b>быстрых</b> игр при генерации выпадения числа в смайлике используются сервера Telegram."
                  "\n"
                    "\nБольше информации здесь - \nhttps://ru.wikipedia.org/wiki/Random.org"
                  "\nhttps://core.telegram.org/api/dice")

    m_question_duel = ("\U0001F93A В режиме Дуэль вы соперничаете с 1 противником. Шанс победить - 50%."
                       "\n" 
                       "\n<b>Побеждаете - забираете его ставку.</b>")

    m_question_russ = ('\U0001F3B2 В режиме Русская рулетка вы соперничаете с 5 противниками. Шанс победить - 16%.'
                       "\n" 
                       "\n<b>Побеждаете - забираете ставки 5 участников.</b>")

    m_question_king = ('\U0001F451 В режиме Королевская битва вы соперничаете с множеством противников, от 6 до 99. '
                       "\n" 
                       "\n<b>Побеждаете - забираете ставки всех участников.</b>")

    m_question_bowl = ("\U0001F3B3 Правила просты \n\nВыбиваете <b>страйк</b> - делаете <b>х2</b>.\nОстается 1 кегля - <b>х1.5</b>"
                       "\nОставшиеся 2 кегли дадут <b>х1.25</b>\nОсталось 3 кегли - <b>x1</b>"
                       "\n\nСбили меньше - увы, ставка не сыграла.")

    m_question_cube = ("\U0001F3B2 Классика всех игр \n\nВ зависимости от выпаших очков ваша ставка умножается на коэффициент:"
                       "\n\n<b>6</b> очков - <b>х2</b>\n<b>5</b> - <b>x1.5</b>\n<b>4</b> - <b>x1.25</b>\n<b>3</b> - <b>x1</b>\n\nМеньше - увы, ставка не сыграла")

    m_question_slot = ("\U0001F3B0 Старый добрый однорукий бандит"
                       "\n\nВыпало <b>777</b> - словили <b>джекпот</b>! Ваша ставка делает <b>х10</b>!"
                       "\nТри \U0001F347, \U0001F34B или <b>BAR</b> - коэффициент <b>х3</b>"
                       "\nЛюбые <b>две 7</b> - Ставка умножается на <b>х2!</b>"
                       "\n<b>Одна 7</b> и <b>два</b> \U0001F347, \U0001F34B или <b>BAR</b> - коэффициент <b>х1.5</b>"
                       "\nДаже если все <b>3 разные</b> - кэшбек с коэффициентом <b>x0.4</b>!"
                       "\n\nВ остальных случаях - увы, ставка не сыграла")

    m_rules = ("\U0001F4CB Использование бота подразумевает согласие с настоящими правилами:"
               "\n"
               "\n1. Админ всегда прав."
               "\n"
               "\n2. Никакой подкрутки нет. Все зависит от рандома."
               "\n"
               "\n3. Ни за что ответственности не несем."
               "\n"
               "\n4. Ничего не возмещаем."
               "\n"
               "\n5. В случае чего сами виноваты.")

    m_enter_requisites_bank = ("<b>Введите номер карты:</b>"
                               "\n\nФормат номера карты - 16 цифр без пробелов и других разделяющих знаков"
                               "\nНапример - <i>4617006599722675</i>")

    m_enter_requisites_qiwi = ("<b>Введите номер телефона:</b>"
                               "\n\nФормат номера телефона - 11 цифр без пробелов и других разделяющих знаков с кодом страны в начале (без + в начале)"
                               "\nНапример - <i>79999224601</i>")

    m_topup_create_1 = ("\U0000267B<b>Ваша транзакция зарегистрирована!</b>"
                            '\n'
                            "\n\U0001F4B8 Для ее выполнения совершите перевод ")

    m_topup_create_2 = ('\n'
                            '\n<b>После</b> выполнения перевода нажмите кнопку ниже')

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

