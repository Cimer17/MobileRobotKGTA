import sqlite3


class DataBase():

    def __init__(self):
        self.conn = sqlite3.connect('diplom.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def check_in_db(self, message):
        self.cursor.execute(f'SELECT name FROM users WHERE user_id = {message.from_user.id}')
        return self.cursor.fetchone()
    
    def check_active_order(self, message):
        self.cursor.execute(f'SELECT code FROM orders WHERE user_id={message.from_user.id} AND status=0')
        return self.cursor.fetchone()
    
    def create_new_order(self, orderinfo):
        self.cursor.execute('INSERT INTO orders VALUES (NULL, ?, ?, ?, ?, ?);', orderinfo)
        self.conn.commit()

    def register_new_user(self, userinfo):
        self.cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?);', userinfo)
        self.conn.commit()
    
    def update_status(self, user):
        self.cursor.execute(f'UPDATE orders SET status=1 WHERE user_id={user}')
        self.conn.commit()