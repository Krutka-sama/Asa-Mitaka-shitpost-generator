import asyncio
import logging
import sys
import re
import random

from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile, BufferedInputFile
from decouple import config
from aiogram import Bot, Dispatcher, types, F
from database import *
from shitpost import shitpost

TOKEN = config('BOT_TOKEN')
NAME = config('DB_NAME')
dp = Dispatcher()

triggers = {
    'ТРАХ': r"\b\w*трах\w*\b",
    'ГОВНО': r"\b\w+(?:core|кор)\b",
    'Планета ТРАХА': r"(?:планет[аеыуо]?\s?техно|пт)\b"

}
chance = 0.1
async def post_random(message: types.Message, chance : float):
    if random.random() <= chance:
        file_id = await get_random_image(message.chat.id)
        text = await get_random_text(message.chat.id)
        if not file_id or not text:
            await message.answer(text="dumbass")
            return
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


@dp.message(Command("Asa_shitpost"))
async def asa_shitpost(message: types.Message):
    if message.reply_to_message:
        try:
            img=message.reply_to_message.photo[-1].file_id
        except:
            img = await get_random_image(message.chat.id)
        text = message.text[19::]
        if not text:
            text = message.reply_to_message.text
            if not text:
                text = await get_random_text(message.chat.id)
    else:
        try:
            img=message.photo[-1].file_id
        except:
            img = await get_random_image(message.chat.id)
            try:
                text = message.caption[19::]
            except:
                text = await get_random_text(message.chat.id)
    if not text or not img:
        await message.answer("nah")
        return
    file_info = await bot.get_file(img)
    image_data = await bot.download_file(file_info.file_path)
    modified_image_buffer = await shitpost(text, image_data)
    img = BufferedInputFile(modified_image_buffer.getvalue(), "shitpost")
    await message.answer_photo(img)
    modified_image_buffer.truncate(0)


@dp.message(F.text)
async def echo_handler(message: types.Message) -> None:
    text = message.text.lower()
    await insert_message(message.chat.id, text)
    for response, pattern in triggers.items():
        if re.search(pattern, text):
            await message.answer(text=response)
            break
    await post_random(message, chance)

@dp.message(F.photo)
async def echo_photo(message: types.Message) -> None:
    await insert_image(message.chat.id, message.photo[-1].file_id)
    await post_random(message, chance)


@dp.message(F.sticker)
async def echo_sticker(message: types.Message) -> None:
    await message.send_copy(chat_id=message.chat.id)
    await post_random(message, chance)


@dp.message(~F.text & ~F.photo & ~F.sticker)
async def echo_any(message: types.Message):
    await post_random(message, chance)

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
