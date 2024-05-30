import sqlite3
from config.settings import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        title TEXT,
                        description TEXT,
                        image_path TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS favorites (
                        user_id INTEGER,
                        event_id INTEGER,
                        FOREIGN KEY(event_id) REFERENCES events(id),
                        UNIQUE(user_id, event_id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS suggestions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        date TEXT,
                        title TEXT,
                        description TEXT,
                        image_path TEXT,
                        status TEXT DEFAULT 'в обработке')''')

    conn.commit()
    conn.close()
