import psycopg2
from datetime import datetime


class BotDB:

    def __init__(self, db_file):
        self.conn = psycopg2.connect(
            host='localhost',
            dbname='lotEasy',
            user='gloub',
            password='1323',
            port=5432)
        self.cursor = self.conn.cursor()

    async def user_exists(self, user_id, arg="user_id"):
        self.cursor.execute(f"SELECT id FROM users WHERE {arg} = %s", (user_id,))
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

    async def rules_accept(self, user_id):
        self.cursor.execute("UPDATE users SET rules_acc = True WHERE user_id = %s", (user_id,))
        return self.conn.commit()

    async def add_user(self, user_id, name, lastname, username):
        self.cursor.execute("INSERT INTO users (user_id, name, lastname, username) VALUES (%s, %s, %s, %s)",
                            (user_id, name, lastname, username))
        return self.conn.commit()

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

    async def topup_balance(self, user_id, sum_topup):
        self.cursor.execute("UPDATE users SET balance = balance+ %s WHERE user_id = %s", (sum_topup, user_id,))
        return self.conn.commit()

    async def withdraw_balance(self, user_id, sum):
        self.cursor.execute("UPDATE users SET balance = balance- %s WHERE user_id = %s", (sum, user_id,))
        return self.conn.commit()

    async def update_data(self, name, lastname, username, user_id):
        self.cursor.execute("UPDATE users SET name = %s, lastname = %s, username = %s  WHERE user_id = %s", (name, lastname, username, user_id,))
        return self.conn.commit()

    async def topup_create(self, user_id, sum_topup, way_topup):
        topup_universal = "INSERT INTO payments (user_id, way_topup, sum) VALUES (%s, %s, %s)"
        self.cursor.execute(topup_universal, (user_id, way_topup, sum_topup,))
        return self.conn.commit()

    async def game_create(self, game, user_id, bet):
        game_create_universal = "INSERT INTO " + game + "_room (user1, bet) VALUES (%s, %s)"
        self.cursor.execute(game_create_universal, (user_id, bet,))
        return self.conn.commit()

    async def game_check_free(self, game, cur_num_user, user_id, bet):
        get_free_game = "SELECT id FROM " + game + "_room WHERE (user1 IS NOT %s AND user1 != %s AND user" + str(cur_num_user) + " IS %s AND bet = %s AND done = %s) order by id DESC LIMIT 1", (None, user_id, None, bet, False)
        self.cursor.execute(*get_free_game)
        return self.cursor.fetchone()

    async def game_get_id(self, game, user_num, user_id, bet):
        get_free_game = "SELECT id FROM " + game + "_room WHERE (user" + str(user_num) + "= %s AND bet = %s) order by id DESC LIMIT 1", (user_id, bet)
        self.cursor.execute(*get_free_game)
        return self.cursor.fetchone()[0]

    async def game_add_user(self, game, cur_user, id_room, user_id, full):
        self.cursor.execute("UPDATE " + game + "_room SET user" + str(cur_user) + " = %s, r_full = %s WHERE id = %s", (user_id, full, id_room,))
        return self.conn.commit()

    async def game_check_full(self, game, id_room):
        get_free_room = "SELECT r_full FROM " + game + "_room WHERE id = %s order by id DESC LIMIT 1", (id_room,)
        self.cursor.execute(*get_free_room)
        return self.cursor.fetchone()[0]

    async def win_num_check(self, game, id_room):
        self.cursor.execute("SELECT num_win FROM " + game + "_room WHERE id = %s", (id_room,))
        return self.cursor.fetchone()[0]

    async def win_num_in(self, game, num_win, id_room):
        self.cursor.execute("UPDATE " + game + "_room SET num_win = %s, done = %s, time_done = %s WHERE id = %s", (num_win, True, str(datetime.now()), id_room,))
        return self.conn.commit()

    async def warned_winner(self, game, id_room):
        self.cursor.execute("UPDATE " + game + "_room SET warned = %s WHERE id = %s", (True, id_room,))
        return self.conn.commit()

    async def with_create(self, user_id, sum_with, way_with, requisites):
        with_universal = "INSERT INTO withdraws (user_id, way_with, sum, requisites) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(with_universal, (user_id, way_with, sum_with, requisites, ))
        return self.conn.commit()

    async def get_topup_lines(self, user_id):
        self.cursor.execute("SELECT COUNT (*) FROM payments WHERE user_id = %s", (user_id,))
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

    async def get_story(self, user_id, num_from):
        self.cursor.execute("SELECT int_pay, way_topup, sum, done, oper, time_create FROM payments WHERE user_id = %s UNION ALL SELECT int_wit, way_with, sum, done, oper, time_create FROM withdraws WHERE user_id = %s ORDER BY time_create DESC OFFSET "+ str(num_from-1) + "ROWS FETCH NEXT 1 ROWS ONLY", (user_id, user_id,))
        return [row for row in self.cursor.fetchone()]

    async def get_lines_no_topup(self):
        self.cursor.execute("SELECT COUNT (*) FROM payments WHERE done = %s", (False, ))
        return self.cursor.fetchone()[0]

    async def get_lines_no_warned(self):
        self.cursor.execute("SELECT COUNT(*) FROM (SELECT id, num_win, warned, game FROM duel_room WHERE (num_win != " + str(0) + " AND warned = " + str(False) + ") UNION ALL SELECT id, num_win, warned, game FROM russ_room WHERE (num_win != " + str(0) + " AND warned = " + str(False) + ") UNION ALL SELECT id, num_win, warned, game FROM king_room WHERE (num_win != " + str(0) + " AND warned = " + str(False) + ")) AS c")
        return self.cursor.fetchone()[0]

    async def get_games_lines(self):
        self.cursor.execute("SELECT COUNT(*) FROM (SELECT id FROM duel_room UNION ALL SELECT id FROM russ_room UNION ALL SELECT id FROM king_room) AS a")
        return self.cursor.fetchone()[0]

    async def all_no_warned_checker(self, M):
        self.cursor.execute("SELECT id, num_win, warned, game FROM duel_room WHERE (num_win != " + str(0) + " AND warned = " + str(False) + ") UNION ALL SELECT id, num_win, warned, game FROM russ_room WHERE (num_win != " + str(0) + " AND warned = " + str(False) + ") UNION ALL SELECT id, num_win, warned, game FROM king_room WHERE (num_win != " + str(0) + " AND warned = " + str(False) + ") ORDER BY id ASC LIMIT 1 OFFSET " + str(M))
        return [row for row in self.cursor.fetchone()]

    async def get_line_game(self, M):
        self.cursor.execute("SELECT id, game, num_win, time_create FROM duel_room UNION ALL SELECT id, game, num_win, time_create UNION ALL SELECT id, game, num_win, time_create FROM king_room ORDER BY id ASC LIMIT 1 OFFSET " + str(M))
        return [row for row in self.cursor.fetchone()]

    async def get_winner(self, id, game, num_win):
        self.cursor.execute("SELECT user" + str(num_win) + ", bet FROM " + game + "_room WHERE id = %s", (id,))
        return [row for row in self.cursor.fetchone()]

    async def all_no_topup_checker(self, M):
        self.cursor.execute("SELECT int_pay, user_id, sum, accrued, done FROM payments WHERE done = " + str(False) + " ORDER BY int_pay ASC LIMIT 1 OFFSET " + str(M))
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

    async def adm_lvl_check(self, user_id):
        self.cursor.execute("SELECT access_lvl FROM admins WHERE adm = %s", (user_id,))
        return self.cursor.fetchone()[0]

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

    async def find_username(self, user_id):
        username_finder = "SELECT username FROM users WHERE user_id = %s", (user_id, )
        self.cursor.execute(*username_finder)
        return self.cursor.fetchone()[0]

    async def update_withd(self, int_wit, way, requisites):
        self.cursor.execute("UPDATE withdraws SET way_with = %s, requisites = %s  WHERE int_wit = %s", (way, requisites, int_wit,))
        return self.conn.commit()

    async def adm_user_info(self, user_id, arg):
        self.cursor.execute(f"SELECT * FROM users WHERE {arg} = %s", (user_id,))
        return [row for row in self.cursor.fetchone()]

    def close(self):
        self.conn.close()

