import psycopg2
from datetime import datetime
from bot.configs.env_reader import env_config


class BotDB:

    def __init__(self):
        self.conn = psycopg2.connect(
            host=env_config.db_host.get_secret_value(),
            dbname=env_config.db_name.get_secret_value(),
            user=env_config.db_user.get_secret_value(),
            password=env_config.db_user_pass.get_secret_value(),
            port=env_config.db_port.get_secret_value())
        self.cursor = self.conn.cursor()

    async def get_user_exists(self, user_id, arg='user_id ='):
        self.cursor.execute(f"SELECT id FROM users WHERE {arg} %s", (user_id,))
        return bool(len(self.cursor.fetchall()))

    async def get_user_id(self, user_id):
        self.cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_user_name(self, user_id):
        self.cursor.execute("SELECT name FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_user_lastname(self, user_id):
        self.cursor.execute("SELECT lastname FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_user_username(self, user_id):
        self.cursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_user_date(self, user_id):
        self.cursor.execute("SELECT join_date FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_rules_accept(self, user_id):
        self.cursor.execute("SELECT rules_acc FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_ban(self, user_id):
        self.cursor.execute("SELECT ban FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def set_rules_accept(self, user_id):
        self.cursor.execute("UPDATE users SET rules_acc = True WHERE user_id = %s", (user_id,))
        return self.conn.commit()

    async def add_user(self, user_id, name, lastname, username):
        self.cursor.execute("INSERT INTO users (user_id, name, lastname, username) VALUES (%s, %s, %s, %s)",
                            (user_id, name, lastname, username))
        return self.conn.commit()

    async def set_user_block_bot(self, user_id, arg):
        self.cursor.execute("UPDATE users SET bot_blocked = %s WHERE user_id = %s", (arg, user_id,))
        return self.conn.commit()

    async def get_bot_block(self, user_id):
        self.cursor.execute("SELECT bot_blocked FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_user_balance(self, user_id):
        self.cursor.execute("SELECT balance FROM users WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_topup_accured(self, top_id):
        self.cursor.execute("SELECT accrued FROM payments WHERE int_pay = %s", (top_id,))
        return self.cursor.fetchone()[0]

    async def get_topup_done(self, top_id):
        self.cursor.execute("SELECT done FROM payments WHERE int_pay = %s", (top_id,))
        return self.cursor.fetchone()[0]

    async def set_topup_done(self, top_id):
        self.cursor.execute("UPDATE payments SET done = True, time_done = %s WHERE int_pay = %s", (str(datetime.now()), top_id,))
        return self.conn.commit()

    async def get_topup_sum(self, top_id):
        self.cursor.execute("SELECT sum FROM payments WHERE int_pay = %s", (top_id,))
        return self.cursor.fetchone()[0]

    async def set_topup_balance(self, user_id, sum_topup):
        self.cursor.execute("UPDATE users SET balance = balance+ %s WHERE user_id = %s", (sum_topup, user_id,))
        return self.conn.commit()

    async def set_withdraw_balance(self, user_id, sum):
        self.cursor.execute("UPDATE users SET balance = balance- %s WHERE user_id = %s", (sum, user_id,))
        return self.conn.commit()

    async def update_data(self, name, lastname, username, user_id):
        self.cursor.execute("UPDATE users SET name = %s, lastname = %s, username = %s  WHERE user_id = %s", (name, lastname, username, user_id,))
        return self.conn.commit()

    async def topup_create(self, user_id, sum_topup, way_topup, requisites):
        topup_universal = "INSERT INTO payments (user_id, way_topup, sum, requisites) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(topup_universal, (user_id, way_topup, sum_topup, requisites))
        return self.conn.commit()

    async def create_room_game(self, game, bet):
        game_create_universal = "INSERT INTO games (game, bet) VALUES (%s, %s)"
        self.cursor.execute(game_create_universal, (game, bet,))
        return self.conn.commit()

    async def check_free_room(self, game, bet, way="ASC"):
        self.cursor.execute("SELECT id_room FROM games WHERE (game = %s AND bet = %s AND is_full = False AND is_end = False) ORDER BY id_room " + way + "", (game, bet,))
        return self.cursor.fetchone()

    async def check_game_end(self, id_room):
        self.cursor.execute("SELECT is_end FROM games WHERE id_room = %s", (id_room,))
        return self.cursor.fetchone()[0]

    async def check_game_full(self, room_id):
        self.cursor.execute("SELECT is_full FROM games WHERE id_room = %s", (room_id,))
        return self.cursor.fetchone()[0]

    async def check_user_second_game(self, room_id, user_id):
        self.cursor.execute("SELECT COUNT (*) FROM game_records WHERE (id_room = %s AND user_id = %s)", (room_id, user_id,))
        return self.cursor.fetchone()[0]

    async def get_games_lines(self,  user_id):
        self.cursor.execute("SELECT COUNT (*) FROM game_records WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def add_user_to_game_room(self, room_id, user_id, user_num, game, bal_before):
        add_user_to_game = "INSERT INTO game_records (id_room, user_id, user_num, game, bal_before) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(add_user_to_game, (room_id, user_id, user_num, game, bal_before))
        return self.conn.commit()

    async def get_no_end_games_lines(self):
        self.cursor.execute("SELECT COUNT(*) FROM games WHERE (is_full = %s, is_end = %s)", (True, False))
        return self.cursor.fetchone()[0]

    async def get_no_warned_player_lines(self):
        self.cursor.execute("SELECT COUNT(*) FROM (SELECT game_records.warned, games.is_end FROM game_records INNER JOIN games ON game_records.id_room = games.id_room WHERE (game_records.warned = False AND games.is_end = True)) AS c")
        return self.cursor.fetchone()[0]

    async def get_all_no_warned_checker(self):
        self.cursor.execute("SELECT game_records.user_id, game_records.user_num, games.id_room, games.game, games.bet, games.win_num, game_records.win_sum, games.time_end FROM game_records INNER JOIN games ON game_records.id_room = games.id_room WHERE (game_records.warned = False AND games.is_end = True) ORDER BY games.id_room ASC FETCH NEXT 1 ROWS ONLY")
        return [row for row in self.cursor.fetchone()]

    async def set_room_full(self, room_id):
        self.cursor.execute("UPDATE games SET is_full = True WHERE id_room = %s", (room_id,))
        return self.conn.commit()

    async def win_num_check(self, room_id):
        self.cursor.execute("SELECT win_num FROM games WHERE id_room = %s", (room_id,))
        return self.cursor.fetchone()[0]

    async def update_win_num_in(self, num_win, id_room):
        self.cursor.execute("UPDATE games SET win_num = %s WHERE id_room = %s", (num_win, id_room, ))
        return self.conn.commit()

    async def update_win_sum_in(self, id_room, user_id, win_sum):
        self.cursor.execute("UPDATE game_records SET win_sum = %s WHERE (id_room = %s AND user_id = %s)", (win_sum, id_room, user_id))
        return self.conn.commit()

    async def warned_winner(self, id_room, user_id):
        self.cursor.execute("UPDATE game_records SET warned = True WHERE (user_id = %s AND id_room = %s)", (user_id, id_room,))
        return self.conn.commit()

    async def set_game_end(self, id_room):
        self.cursor.execute("UPDATE games SET is_end = True, time_end = %s WHERE id_room = %s", (str(datetime.now()), id_room))
        return self.conn.commit()

    async def with_create(self, user_id, sum_with, way_with, requisites):
        with_universal = "INSERT INTO withdraws (user_id, way_with, sum, requisites) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(with_universal, (user_id, way_with, sum_with, requisites, ))
        return self.conn.commit()

    async def get_topup_lines(self, user_id):
        self.cursor.execute("SELECT COUNT (*) FROM payments WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_user_num(self, id_room):
        self.cursor.execute("SELECT COUNT (*) FROM game_records WHERE id_room = %s", (id_room,))
        return self.cursor.fetchone()[0]

    async def get_topups_user(self, user_id):
        self.cursor.execute("SELECT * FROM payments WHERE user_id = %s ORDER BY int_pay DESC LIMIT 1", (user_id,))
        return [row for row in self.cursor.fetchone()]

    async def get_withd_lines(self, user_id):
        self.cursor.execute("SELECT COUNT (*) FROM withdraws WHERE user_id = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def get_comm(self, user_id, sum_topup, way_topup):
        comm_universal = "SELECT int_pay FROM payments WHERE (user_id = %s AND sum = %s AND way_topup = %s) order by int_pay DESC LIMIT 1", (user_id, sum_topup, way_topup)
        self.cursor.execute(*comm_universal)
        return self.cursor.fetchone()[0]

    async def get_with(self, user_id, sum_with, way_with):
        comm_universal = "SELECT int_wit FROM withdraws WHERE (user_id = %s AND sum = %s AND way_with = %s) order by int_wit DESC LIMIT 1", (user_id, sum_with, way_with)
        self.cursor.execute(*comm_universal)
        return self.cursor.fetchone()[0]

    async def get_requisites(self, comm):
        comm_universal = "SELECT requisites FROM withdraws WHERE int_wit = %s", (comm, )
        self.cursor.execute(*comm_universal)
        return self.cursor.fetchone()[0]

    async def message_saver(self, msg_id, user_id, msg_data):
        self.cursor.execute("INSERT INTO messages (msg_id_tg, user_id, msg_data) VALUES (%s, %s, %s)",
                            (msg_id, user_id, msg_data))
        return self.conn.commit()

    async def get_story_oper(self, user_id, num_from):
        self.cursor.execute("SELECT int_pay, way_topup, sum, done, oper, time_create FROM payments WHERE user_id = %s UNION ALL "
                            "SELECT int_wit, way_with, sum, done, oper, time_create FROM withdraws WHERE user_id = %s ORDER BY time_create DESC OFFSET "+ str(num_from-1) + "ROWS FETCH NEXT 1 ROWS ONLY", (user_id, user_id,))
        return [row for row in self.cursor.fetchone()]

    async def get_story_game(self, user_id, num_from):
        self.cursor.execute("SELECT game_records.user_num, game_records.warned, game_records.win_sum, game_records.bal_before,"
                            "games.id_room, games.win_num, games.is_full, games.is_end, games.time_create, games.time_end, games.bet, games.game "
                            "FROM game_records INNER JOIN games ON game_records.id_room = games.id_room WHERE user_id = %s ORDER BY games.time_create DESC OFFSET "+ str(num_from-1) + "ROWS FETCH NEXT 1 ROWS ONLY", (user_id,))
        return [row for row in self.cursor.fetchone()]

    async def get_lines_no_topup(self):
        self.cursor.execute("SELECT COUNT (*) FROM payments WHERE done = false")
        return self.cursor.fetchone()[0]

    async def get_lines_not_done_topup(self):
        self.cursor.execute("SELECT COUNT (*) FROM payments WHERE (accrued = true and done = false)")
        return self.cursor.fetchone()[0]

    async def all_no_topup_checker(self):
        self.cursor.execute("SELECT int_pay, user_id, sum, accrued, done FROM payments WHERE (accrued = True AND done = False) ORDER BY int_pay ASC FETCH NEXT 1 ROWS ONLY")
        return [row for row in self.cursor.fetchone()]

    async def get_withd_way(self, withd_id):
        self.cursor.execute("SELECT way_with FROM withdraws WHERE int_wit = %s", (withd_id,))
        return self.cursor.fetchone()[0]

    async def adm_check(self, user_id):
        self.cursor.execute("SELECT id FROM admins WHERE adm = %s", (user_id,))
        return bool(len(self.cursor.fetchall()))

    async def adm_valid_check(self, user_id):
        self.cursor.execute("SELECT valid FROM admins WHERE adm = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def set_adm_valid(self, user_id, arg):
        self.cursor.execute("UPDATE admins SET valid = %s WHERE adm = %s", (arg, user_id,))
        return self.conn.commit()

    async def set_adm_lvl(self, user_id, new_lvl):
        self.cursor.execute("UPDATE admins SET access_lvl = %s WHERE adm = %s", (new_lvl, user_id,))
        return self.conn.commit()

    async def adm_lvl_check(self, user_id):
        self.cursor.execute("SELECT access_lvl FROM admins WHERE adm = %s", (user_id,))
        return self.cursor.fetchone()[0]

    async def adm_add_admin(self, user_id, inviter):
        self.cursor.execute("INSERT INTO admins (adm, inviter, valid) VALUES (%s, %s, %s)", (user_id, inviter, True))
        return self.conn.commit()

    async def adm_info_topup(self, id_pay):
        self.cursor.execute("SELECT * FROM payments WHERE int_pay = %s", (id_pay,))
        return [row for row in self.cursor.fetchone()]

    async def adm_info_withd(self, id_pay):
        self.cursor.execute("SELECT * FROM withdraws WHERE int_wit = %s", (id_pay,))
        return [row for row in self.cursor.fetchone()]

    async def adm_topup_true(self, trans_id):
        self.cursor.execute("UPDATE payments SET accrued = True WHERE int_pay = %s", (trans_id,))
        return self.conn.commit()

    async def adm_withd_true(self, trans_id):
        self.cursor.execute("UPDATE withdraws SET done = True, time_done = %s WHERE int_wit = %s", (str(datetime.now()), trans_id,))
        return self.conn.commit()

    async def adm_find_username(self, user_id):
        username_finder = "SELECT username FROM users WHERE user_id = %s", (user_id, )
        self.cursor.execute(*username_finder)
        return self.cursor.fetchone()[0]

    async def adm_update_withd(self, int_wit, way, requisites):
        self.cursor.execute("UPDATE withdraws SET way_with = %s, requisites = %s  WHERE int_wit = %s", (way, requisites, int_wit,))
        return self.conn.commit()

    async def adm_user_info(self, user_id, arg="user_id ="):
        self.cursor.execute(f"SELECT * FROM users WHERE {arg} %s", (user_id,))
        return [row for row in self.cursor.fetchone()]

    async def get_admin_lines(self):
        self.cursor.execute("SELECT COUNT(*) FROM admins")
        return self.cursor.fetchone()[0]

    async def adm_adm_info(self, user_id):
        self.cursor.execute(f"SELECT * FROM admins WHERE adm = %s", (user_id,))
        return [row for row in self.cursor.fetchone()]

    async def adm_list_info(self, M):
        self.cursor.execute(f"SELECT id, adm, valid, access_lvl FROM admins ORDER BY id DESC OFFSET " + str(M-1) + "ROWS FETCH NEXT 1 ROWS ONLY")
        return [row for row in self.cursor.fetchone()]

    async def adm_ban_user(self, user_id, arg):
        self.cursor.execute("UPDATE users SET ban = %s WHERE user_id = %s", (arg, user_id,))
        return self.conn.commit()

    async def adm_nul_balance(self, user_id):
        self.cursor.execute("UPDATE users SET balance = 0 WHERE user_id = %s", (user_id,))
        return self.conn.commit()

    async def adm_set_balance(self, user_id, balance):
        self.cursor.execute("UPDATE users SET balance = %s WHERE user_id = %s", (balance, user_id,))
        return self.conn.commit()

    def close(self):
        print("Db closed")
        self.conn.close()

