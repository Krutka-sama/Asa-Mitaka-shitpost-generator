import asyncio
import logging
import sys
import re
import random

from aiogram.filters import CommandStart
from aiogram.types import FSInputFile, BufferedInputFile
from decouple import config
from aiogram import Bot, Dispatcher, types, F
from database import connect, close, create_table, insert_text, insert_image, increment_count, get_image, get_text
from shitpost import shitpost

TOKEN = config('BOT_TOKEN')
NAME = config('DB_NAME')
dp = Dispatcher()

triggers = {
    'ТРАХ': r"\b\w*трах\w*\b",
    'ГОВНО': r"\b\w+(?:core|кор)\b",
    'Планета ТРАХА': r"(?:планет[аеыуо]?\s?техно|пт)\b"

}
@dp.message(CommandStart())
async def start(message: types.Message):
    file_id = await get_image(message.chat.id)
    text = await get_text(message.chat.id)
    file_info = await bot.get_file(file_id)

    # path = "img/" + str(message.chat.id) + ".png"
    # await bot.download_file(file_info.file_path, path)
    # await shitpost(text, path)
    # photo = FSInputFile(path)
    # await message.answer_photo(photo)

    #I have no idea how to use streams in python so this is probably trash garbage shit curse death
    image_data = await bot.download_file(file_info.file_path)
    modified_image_buffer = await shitpost(text, image_data)
    img=BufferedInputFile(modified_image_buffer.getvalue(), "shitpost")
    await message.answer_photo(img)
    modified_image_buffer.truncate(0)


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
    global bot
    bot = Bot(TOKEN)
    await connect(NAME)
    await create_table()
    try:
        await dp.start_polling(bot)
    except:
        await close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
