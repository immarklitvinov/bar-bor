import sqlite3


class SQLighter2:
    def __init__(self, database_file):
        "Подключаемся к БД и сохраняем курсор соединения"
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def add_message(self, user_id, bar_id, list_of_people, current_user):
        with self.connection:
            return self.cursor.execute(
                "INSERT INTO messages (user_id, bar_id, list_of_people, current_user) VALUES (?, ?, ?, ?)",
                (user_id, bar_id, list_of_people, current_user))

    def set_people(self, user_id, bar_id, list_of_people):
        with self.connection:
            list_of_people = str(list_of_people)
            return self.cursor.execute("UPDATE messages SET list_of_people = ? WHERE user_id = ? and bar_id = ?",
                                       (list_of_people, user_id, bar_id)), self.connection.commit()

    def set_new_people(self, current_user, user_id, bar_id):
        with self.connection:
            return self.cursor.execute("UPDATE messages SET current_user = ? WHERE user_id = ? and bar_id = ?",
                                       (current_user, user_id, bar_id)), self.connection.commit()

    def get_current_user(self, user_id, bar_id):
        with self.connection:
            return self.cursor.execute("SELECT current_user from messages WHERE user_id = ? and bar_id = ?", (user_id, bar_id)).fetchall()

    def get_people(self, user_id, bar_id):
        with self.connection:
            return self.cursor.execute("SELECT list_of_people from messages WHERE user_id = ? and bar_id = ?",
                                       (user_id, bar_id)).fetchall()

    def deleter(self, user_id):
        with self.connection:
            user_id = str(user_id)
            return self.cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,)), self.connection.commit()

    def close(self):
        "Закрываем соединение с бд"
        self.connection.close()
