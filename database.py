import sqlite3
from decouple import config
from emoji import replace_emoji

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
                               chat_id INTEGER NOT NULL,
                               message TEXT NOT NULL, UNIQUE(chat_id, message)
                           )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS image (
                               id INTEGER PRIMARY KEY,
                               chat_id INTEGER NOT NULL,
                               image TEXT NOT NULL, UNIQUE(chat_id, image)
                           )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ban (
                               id INTEGER PRIMARY KEY,
                               chat_id INTEGER NOT NULL UNIQUE
                            )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                               id INTEGER PRIMARY KEY,
                               chat_id INTEGER NOT NULL UNIQUE,
                               SIZE_LAT INTEGER NOT NULL,
                               CHANCE REAL NOT NULL,
                               CHANCE_STICKER REAL NOT NULL,
                               CHANCE_SAY REAL NOT NULL,
                               CHANCE_SKIP REAL NOT NULL
                           )''')


async def insert_message(chat_id: int, message: str, max_rows=M_SCOPE):
    message = replace_emoji(message, "")
    if message:
        cursor.execute("SELECT COUNT(*) FROM message WHERE chat_id = ? AND message = ?", (chat_id, message))
        num_rows = cursor.fetchone()[0]
        if not num_rows:
            cursor.execute("INSERT INTO message (chat_id, message) VALUES (?, ?)", (chat_id, message))
            cursor.connection.commit()

            cursor.execute("SELECT COUNT(*) FROM message WHERE chat_id = ?", (chat_id,))
            num_chat_rows = cursor.fetchone()[0]

            if num_chat_rows > max_rows:
                cursor.execute(
                    f"DELETE FROM message WHERE id IN (SELECT id FROM message WHERE chat_id = ? ORDER BY id ASC LIMIT {num_chat_rows - max_rows})",
                    (chat_id,))
                cursor.connection.commit()


async def insert_image(chat_id: int, image: str, max_rows=I_SCOPE):
    cursor.execute("SELECT COUNT(*) FROM image WHERE chat_id = ? AND image = ?", (chat_id, image))
    num_rows = cursor.fetchone()[0]
    if not num_rows:
        cursor.execute("INSERT INTO image (chat_id, image) VALUES (?, ?)", (chat_id, image))
        cursor.connection.commit()

        cursor.execute("SELECT COUNT(*) FROM image WHERE chat_id = ?", (chat_id,))
        num_image_rows = cursor.fetchone()[0]

        if num_image_rows > max_rows:
            cursor.execute(
                f"DELETE FROM image WHERE id IN (SELECT id FROM image WHERE chat_id = ? ORDER BY id ASC LIMIT {num_image_rows - max_rows})",
                (chat_id,))
            cursor.connection.commit()


async def get_random_text(chat_id: int):
    cursor.execute("SELECT message FROM message WHERE chat_id = ? ORDER BY RANDOM() LIMIT 1", (chat_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return None


async def get_random_image(chat_id: int):
    cursor.execute("SELECT image FROM image WHERE chat_id = ? ORDER BY RANDOM() LIMIT 1", (chat_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return None


async def delete_message(chat_id: int, message: str):
    message = replace_emoji(message, "").lower()
    if message:
        cursor.execute("SELECT COUNT(*) FROM message WHERE chat_id = ? AND message = ?", (chat_id, message))
        num_rows = cursor.fetchone()[0]
        if num_rows > 0:
            cursor.execute("DELETE FROM message WHERE chat_id = ? AND message = ?", (chat_id, message))
            cursor.connection.commit()
            return True
        else:
            return False
    else:
        return False


async def delete_image(chat_id: int, image: str):
    cursor.execute("SELECT COUNT(*) FROM image WHERE chat_id = ? AND image = ?", (chat_id, image))
    num_rows = cursor.fetchone()[0]
    if num_rows > 0:
        cursor.execute("DELETE FROM image WHERE chat_id = ? AND image = ?", (chat_id, image))
        cursor.connection.commit()
        return True
    else:
        return False


async def delete_all_messages(chat_id: int):
    cursor.execute("DELETE FROM message WHERE chat_id = ?", (chat_id,))
    cursor.connection.commit()


async def delete_all_images(chat_id: int):
    cursor.execute("DELETE FROM image WHERE chat_id = ?", (chat_id,))
    cursor.connection.commit()


async def get_banned() -> list[int]:
    cursor.execute("SELECT chat_id FROM ban")
    rows = cursor.fetchall()
    return [row[0] for row in rows]


async def ban(chat_id: int):
    cursor.execute("INSERT INTO ban (chat_id) VALUES (?)", (chat_id,))
    cursor.connection.commit()


async def unban(chat_id: int):
    cursor.execute("DELETE FROM ban WHERE chat_id = ?", (chat_id,))
    cursor.connection.commit()


async def get_all_settings():
    cursor.execute("SELECT chat_id, SIZE_LAT, CHANCE, CHANCE_STICKER, CHANCE_SAY, CHANCE_SKIP FROM settings")
    rows = cursor.fetchall()
    settings = {row[0]: row[1:] for row in rows}
    return settings


async def set_settings(chat_id: int, data: list):
    cursor.execute(
        "INSERT OR REPLACE INTO settings (chat_id, SIZE_LAT, CHANCE, CHANCE_STICKER, CHANCE_SAY, CHANCE_SKIP) VALUES (?, ?, ?, ?, ?, ?)",
        (chat_id, *data))
    cursor.connection.commit()


async def delete_settings(chat_id: int):
    cursor.execute("DELETE FROM settings WHERE chat_id=?", (chat_id,))
    cursor.connection.commit()
