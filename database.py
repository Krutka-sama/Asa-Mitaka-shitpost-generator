import sqlite3
from decouple import config
M_SCOPE = int(config('MESSAGES_SCOPE'))
I_SCOPE = int(config('IMAGES_SCOPE'))


async def connect(db_name):
    global db, cursor
    db = sqlite3.connect(db_name)
    cursor = db.cursor()


async def close():
    db.close()


async def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS message (
                               id INTEGER PRIMARY KEY,
                               chat_id INTEGER,
                               text TEXT
                           )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS image (
                               id INTEGER PRIMARY KEY,
                               chat_id INTEGER,
                               image TEXT
                           )''')

    # cursor.execute('''CREATE TABLE IF NOT EXISTS ban (
    #                         id INTEGER PRIMARY KEY,
    #                         chat_id INTEGER UNIQUE
    #                     )''')
    # cursor.connection.commit()


async def insert_message(chat_id, text, max_rows=M_SCOPE):
    cursor.execute("INSERT INTO message (chat_id, text) VALUES (?, ?)", (chat_id, text))
    cursor.connection.commit()

    cursor.execute("SELECT COUNT(*) FROM message WHERE chat_id = ?", (chat_id,))
    num_chat_rows = cursor.fetchone()[0]

    if num_chat_rows > max_rows:
        cursor.execute(
            f"DELETE FROM message WHERE id IN (SELECT id FROM message WHERE chat_id = ? ORDER BY id ASC LIMIT {num_chat_rows - max_rows})",
            (chat_id,))
        cursor.connection.commit()


async def insert_image(chat_id, image, max_rows=I_SCOPE):
    cursor.execute("INSERT INTO image (chat_id, image) VALUES (?, ?)", (chat_id, image))
    cursor.connection.commit()

    cursor.execute("SELECT COUNT(*) FROM image WHERE chat_id = ?", (chat_id,))
    num_image_rows = cursor.fetchone()[0]

    if num_image_rows > max_rows:
        cursor.execute(
            f"DELETE FROM image WHERE id IN (SELECT id FROM image WHERE chat_id = ? ORDER BY id ASC LIMIT {num_image_rows - max_rows})",
            (chat_id,))
        cursor.connection.commit()


async def get_random_text(chat_id):
    cursor.execute("SELECT text FROM message WHERE chat_id = ? ORDER BY RANDOM() LIMIT 1", (chat_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return None


async def get_random_image(chat_id):
    cursor.execute("SELECT image FROM image WHERE chat_id = ? ORDER BY RANDOM() LIMIT 1", (chat_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return None
