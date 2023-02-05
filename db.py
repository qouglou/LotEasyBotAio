import psycopg2
from datetime import datetime

hostname = 'localhost'
database = 'lotEasy'
username = 'gloub'
password = '1323'
port_id = 5432


class BotDB:

    def __init__(self, db_file):
        self.conn = psycopg2.connect(
            host = hostname,
            dbname = database,
            user = username,
            password = password,
            port = port_id)
        self.cursor = self.conn.cursor()

    async def user_exists(self, user_id):
        self.cursor.execute("SELECT id FROM users WHERE user_id = %s", (user_id,))
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
        date = datetime.now()
        self.cursor.execute("UPDATE payments SET done = True, time_done = %s WHERE int_pay = %s", (str(date), top_id,))
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
        date = datetime.now()
        self.cursor.execute("UPDATE " + game + "_room SET num_win = %s, done = %s, time_done = %s WHERE id = %s", (num_win, True, str(date), id_room,))
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
        payments = self.cursor.fetchall()
        for row in payments:
            Id = row[0]
            User = row[1]
            Way = row[2]
            Sum = row[3]
            time_cr = row[4]
        return [Id, User, Way, Sum, time_cr]

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

    async def message_up_delete(self, msg_id):
        self.cursor.execute("UPDATE messages SET deleted = True, WHERE msg_id_t = %s",
                            (msg_id))
        return self.conn.commit()

    async def get_story(self, user_id, N):
        self.cursor.execute("SELECT int_pay, way_topup, sum, done, oper, time_create FROM payments WHERE user_id = %s UNION ALL SELECT int_wit, way_with, sum, done, oper, time_create FROM withdraws WHERE user_id = %s ORDER BY time_create DESC LIMIT "+ str(1) + " OFFSET " + str(N-1), (user_id, user_id,))
        lines = self.cursor.fetchall()
        for row in lines:
            Id = row[0]
            Way = row[1]
            Sum = row[2]
            Done = row[3]
            Oper = row[4]
            Time_cr = row[5]
        return [Id, Way, Sum, Done, Oper, Time_cr]

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
        lines = self.cursor.fetchall()
        for row in lines:
            id = row[0]
            num_win = row[1]
            warned = row[2]
            game = row[3]
        return [id, num_win, warned, game]

    async def get_line_game(self, M):
        self.cursor.execute("SELECT id, game, num_win, time_create FROM duel_room UNION ALL SELECT id, game, num_win, time_create UNION ALL SELECT id, game, num_win, time_create FROM king_room ORDER BY id ASC LIMIT 1 OFFSET " + str(M))
        lines = self.cursor.fetchall()
        for row in lines:
            id = row[0]
            game = row[1]
            num_win = row[2]
            time_create = row[3]
        return [id, game, num_win, time_create]

    async def get_winner(self, id, game, num_win):
        self.cursor.execute("SELECT user" + str(num_win) + ", bet FROM " + game + "_room WHERE id = %s", (id,))
        lines = self.cursor.fetchall()
        for row in lines:
            user_id = row[0]
            bet = row[1]
        return [user_id, bet]

    async def all_no_topup_checker(self, M):
        self.cursor.execute("SELECT int_pay, user_id, sum, accrued, done FROM payments WHERE done = " + str(False) + " ORDER BY int_pay ASC LIMIT 1 OFFSET " + str(M))
        lines = self.cursor.fetchall()
        for row in lines:
            int_pay = row[0]
            user_id = row[1]
            sum = row[2]
            accrued = row[3]
            done = row[4]
        return [int_pay, user_id, sum, accrued, done]

    async def adm_check(self, user_id):
        self.cursor.execute("SELECT id FROM admins WHERE adm = %s", (user_id,))
        return bool(len(self.cursor.fetchall()))

    async def adm_valid_check(self, user_id):
        self.cursor.execute("SELECT valid FROM admins WHERE adm = %s", (user_id,))
        return self.cursor.fetchone()[0]

    def close(self):
        self.conn.close()

