import sqlite3


class SQLighter:
    def __init__(self, database_file):
        "Подключаемся к БД и сохраняем курсор соединения"
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def get_phone(self, user_id):
        "В таблице ли номер"
        with self.connection:
            result = self.cursor.execute("SELECT phonenumber FROM users WHERE user_id = ?", (user_id,)).fetchall()
            result = str(result[0])
            if '?' in result:
                return result[2:len(result) - 3]
            else:
                return result[1:-2]

    def get_phone1(self, user_name):
        "В таблице ли номер"
        with self.connection:
            result = self.cursor.execute("SELECT phonenumber FROM users WHERE username = ?", (user_name,)).fetchall()
            result = str(result[0])
            if '?' in result:
                return result[2:len(result) - 3]
            else:
                return result[1:-2]

    def get_subscriptions(self, status=True):
        "Активные подписчики бота"
        with self.connection:
            return self.cursor.execute("SELECT * FROM users WHERE status = ?", (status,)).fetchall()

    def subscriber_exists(self, user_id):
        "В базе ли юзер"
        with self.connection:
            result = self.cursor.execute("SELECT *  FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status=True, fullname='Петя', username='bot', phonenumber='?'):
        "Добавить подписчика"
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO users (user_id, status, fullname, username, phonenumber) VALUES (?, ?, ?, ?, ?)",
                (user_id, status, fullname, username, phonenumber))

    def update_subscription(self, user_id, status, fullname, username, phonenumber):
        "Статус подписки"
        return self.cursor.execute(
            "UPDATE users SET status = ?, fullname = ?, username = ?, phonenumber = ? WHERE user_id = ?",
            (status, fullname, username, phonenumber, user_id)), self.connection.commit()

    def update_regged_bar(self, user_id, bar_going):
        return self.cursor.execute("UPDATE users SET bar_going = ? WHERE user_id = ?",
                                   (bar_going, user_id,)), self.connection.commit()

    def users_bar(self, user_id):
        with self.connection:
            return str(self.cursor.execute("SELECT bar_going FROM users WHERE user_id = ?", (user_id,)).fetchall())

    def get_username(self, user_id):
        with self.connection:
            s = str(self.cursor.execute("SELECT username FROM users WHERE user_id = ?", (user_id,)).fetchall())
            return '@' + s[3:-4]

    def get_user_age(self, username):
        with self.connection:
            s = str(self.cursor.execute("SELECT age FROM users WHERE username = ?", (username,)).fetchall())
            return s[2:-3]

    def get_user_sex(self, username):
        with self.connection:
            s = str(self.cursor.execute("SELECT male FROM users WHERE username= ?", (username,)).fetchall())
            s = s[3: -4]
            if s == 'male':
                s = 'парень 🧑'
            else:
                s = 'девушка 👩'
            return s

    def get_photo(self, username):
        with self.connection:
            s = self.cursor.execute("SELECT photo FROM users WHERE username = ?", (username,)).fetchall()
            return s

    def get_fullname(self, username):
        with self.connection:
            s = self.cursor.execute("SELECT fullname FROM users WHERE username = ?", (username,)).fetchall()
            return s

    def clear_all_users_bars(self):
        with self.connection:
            return self.cursor.execute("UPDATE users SET bar_going = '' "), self.connection.commit()

    def users_bar_to_go(self, username):
        with self.connection:
            s = str(self.cursor.execute("SELECT bar_going FROM users WHERE username = ?", (username,)).fetchall())
            if s != '[]':
                s = s[2: -3]
            else:
                s = 'no_user'
            return s

    def add_user_photo(self, user_id, photo):
        with self.connection:
            return self.cursor.execute("UPDATE users SET photo = ? WHERE user_id = ?",
                                       (photo, user_id,)), self.connection.commit()

    def add_user_age(self, user_id, age):
        with self.connection:
            return self.cursor.execute("UPDATE users SET age = ? WHERE user_id = ?",
                                       (age, user_id,)), self.connection.commit()

    def add_user_male(self, user_id, male):
        with self.connection:
            return self.cursor.execute("UPDATE users SET male = ? WHERE user_id = ?",
                                       (male, user_id,)), self.connection.commit()

    def get_l(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT l from users WHERE user_id = ?",
                                       (user_id,)).fetchall()

    def set_l(self, l, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET l = ? WHERE user_id = ?",
                                       (l, user_id)), self.connection.commit()

    def get_l1(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT l1 from users WHERE user_id = ?",
                                       (user_id,)).fetchall()

    def set_l1(self, l1, user_id):
        with self.connection:
            return self.cursor.execute("UPDATE users SET l1 = ? WHERE user_id = ?",
                                       (l1, user_id)), self.connection.commit()

    def close(self):
        "Закрываем соединение с бд"
        self.connection.close()

    def delete_all(self):
        with self.connection:
            return self.cursor.execute("DELETE FROM users")


# db_users = SQLighter('users.db')
# db_users.delete_all