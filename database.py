import sqlite3
async def connect(db_name):
    global db, cursor
    db = sqlite3.connect(db_name)
    cursor = db.cursor()

async def close():
    db.close()

async def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS chat (
                            id INTEGER PRIMARY KEY,
                            chat_id INTEGER UNIQUE,
                            text TEXT,
                            image TEXT,
                            count INTEGER DEFAULT 0
                        )''')
    cursor.connection.commit()

async def check_chat_id(chat_id):
    cursor.execute("SELECT * FROM chat WHERE chat_id = ?", (chat_id,))
    existing_chat = cursor.fetchone()
    if not existing_chat:
        cursor.execute("INSERT INTO chat (chat_id) VALUES (?)", (chat_id,))
        cursor.connection.commit()

async def insert_text(chat_id, text):
    cursor.execute("UPDATE chat SET text = ? WHERE chat_id = ?",
                         (text, chat_id))
    cursor.connection.commit()

async def insert_image(chat_id, image):
    cursor.execute("UPDATE chat SET image = ? WHERE chat_id = ?",
                         (image, chat_id))
    cursor.connection.commit()

async def increment_count(chat_id):
    await check_chat_id(chat_id)
    cursor.execute("UPDATE chat SET count = count + 1 WHERE chat_id = ?",
                         (chat_id,))
    cursor.connection.commit()

async def reset_count(chat_id):
    await check_chat_id(chat_id)
    cursor.execute("UPDATE chat SET count = 0 WHERE chat_id = ?",
                         (chat_id,))
    cursor.connection.commit()

async def get_text(chat_id):
    cursor.execute("SELECT text FROM chat WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return None

async def get_image(chat_id):
    cursor.execute("SELECT image FROM chat WHERE chat_id = ?", (chat_id,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return None
