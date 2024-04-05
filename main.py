import asyncio
import logging
import sys
import re
import random
from decouple import config
from aiogram import Bot, Dispatcher, Router, types, F
from database import connect, create_table, insert_text, insert_image, increment_count

TOKEN = config('BOT_TOKEN')
NAME = config('DB_NAME')
dp = Dispatcher()

triggers = {
    'ТРАХ': r"\b\w*трах\w*\b",
    'ГОВНО': r"\b\w+(?:core|кор)\b",
    'Планета ТРАХА': r"(?:планет[аеыуо]?\s?техно|пт)\b"

}


@dp.message(F.text)
async def echo_handler(message: types.Message) -> None:
    text = message.text.lower()
    await increment_count(message.chat.id)
    await insert_text(message.chat.id, text)
    for response, pattern in triggers.items():
        if re.search(pattern, text):
            await message.answer(text=response)
            break


@dp.message(F.photo)
async def echo_photo(message: types.Message) -> None:
    await increment_count(message.chat.id)
    await insert_image(message.chat.id, message.photo[-1].file_id)


@dp.message(F.sticker)
async def echo_sticker(message: types.Message) -> None:
    await increment_count(message.chat.id)
    await message.send_copy(chat_id=message.chat.id)


@dp.message(~F.text & ~F.photo & ~F.sticker)
async def echo_any(message: types.Message):
    await increment_count(message.chat.id)


async def main() -> None:
    bot = Bot(TOKEN)
    await connect(NAME)
    await create_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
