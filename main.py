import asyncio
import logging
import sys
import re
from random import random, shuffle, choice
from aiogram.filters import CommandStart, Command
from aiogram.types import BufferedInputFile
# from aiogram.types import FSInputFile
from decouple import config
from aiogram import Bot, Dispatcher, types, F
from database import create_table, connect, close, insert_message, insert_image, get_random_text, get_random_image, \
    delete_message, delete_image, delete_all_messages, delete_all_images
from shitpost import shitpost
from stuff import *

TOKEN = config('BOT_TOKEN')
NAME = config('DB_NAME')
OWNER = config('OWNER_ID')
SIZE_LAT = int(config('DEFAULT_SIZE_LAT'))
CHANCE = float(config('DEFAULT_CHANCE'))
CHANCE_STICKER = float(config('DEFAULT_CHANCE_STICKER'))
CHANCE_SAY = float(config('DEFAULT_CHANCE_SAY'))
dp = Dispatcher()


async def say_stuff(message: types.Message, chance: float):
    if random() <= chance:
        text = await get_random_text(message.chat.id)
        if not text:
            await message.answer("Fuck you")
            return
        text = text.split(" ")
        shuffle(text)
        answer = ""
        for i in text:
            answer += i
            answer += " "
        await message.answer(answer.capitalize())


async def post_random(message: types.Message, chance: float):
    if random() <= chance:
        file_id = await get_random_image(message.chat.id)
        text = await get_random_text(message.chat.id)
        if not file_id or not text:
            await message.answer("Dumbass")
            return
        file_info = await bot.get_file(file_id)

        # path = "img/" + str(message.chat.id) + ".png"
        # await bot.download_file(file_info.file_path, path)
        # await shitpost(text, path)
        # photo = FSInputFile(path)
        # await message.answer_photo(photo)

        # I have no idea how to use streams in python so this is probably trash garbage shit curse death
        image_data = await bot.download_file(file_info.file_path)
        modified_image_buffer = await shitpost(text, image_data, SIZE_LAT)
        img = BufferedInputFile(modified_image_buffer.getvalue(), "shitpost")
        await message.answer_photo(img)
        modified_image_buffer.truncate(0)


async def post_femcel(message: types.Message, chance: float):
    if random() <= chance:
        try:
            await message.answer_sticker(choice(femcel))
        except:
            pass


@dp.message(CommandStart())
async def command_start_handler(message: types.Message):
    await message.answer(f"Hi, {message.from_user.full_name}, Im Asa Mitaka. Im autistic and I love shitposting!\n\n"
                         f"Use /Asa_shitpost to create a shitpost from last random 100 messages and pics,"
                         f" you can also send me a pic directly or reply to one with the same command"
                         f" to create post with the pic you want, it works with text too!\n\n"
                         f"Use /Asa_delete_message and /Asa_delete_image"
                         f" to get rid of unwanted pictures and signatures!\n\n"
                         f"I work only with latin and cyrillic characters!!! And i wont display emoji!!!")


@dp.message(Command("Asa_shitpost"))
async def asa_shitpost(message: types.Message):
    if message.reply_to_message:
        try:
            img = message.reply_to_message.photo[-1].file_id
        except:
            img = await get_random_image(message.chat.id)
        text = message.text[13::]
        if not text:
            text = message.reply_to_message.text
            if not text:
                text = message.reply_to_message.caption
                if not text:
                    text = await get_random_text(message.chat.id)
    else:
        try:
            img = message.photo[-1].file_id
        except:
            img = await get_random_image(message.chat.id)
        try:
            text = message.caption[13::]
            if not text:
                try:
                    text = message.text[13::]
                    if not text:
                        text = await get_random_text(message.chat.id)
                except:
                    text = await get_random_text(message.chat.id)
        except:
            text = message.text[13::]
            if not text:
                text = await get_random_text(message.chat.id)
    if not text or not img:
        await message.answer("Nah")
        return
    file_info = await bot.get_file(img)
    image_data = await bot.download_file(file_info.file_path)
    modified_image_buffer = await shitpost(text, image_data, SIZE_LAT)
    img = BufferedInputFile(modified_image_buffer.getvalue(), "shitpost")
    await message.answer_photo(img)
    modified_image_buffer.truncate(0)


@dp.message(Command("Asa_delete_message"))
async def asa_delete_message(message: types.Message):
    if message.reply_to_message:
        text = message.text[20::]
        if not text:
            text = message.reply_to_message.text
            if not text:
                text = message.reply_to_message.caption
                if not text:
                    text = None
    else:
        try:
            text = message.caption[20::]
            if not text:
                try:
                    text = message.text[20::]
                    if not text:
                        text = None
                except:
                    text = None
        except:
            text = message.text[20::]
            if not text:
                text = None
    if text:
        if await delete_message(message.chat.id, text):
            await message.answer(f'"{text}" deleted, bye bye')
        else:
            await message.answer(f'idk what "{text}" is')
    else:
        await message.answer("???")


@dp.message(Command("Asa_delete_image"))
async def asa_delete_image(message: types.Message):
    if message.reply_to_message:
        try:
            img = message.reply_to_message.photo[-1].file_id
        except:
            img = None
    else:
        try:
            img = message.photo[-1].file_id
        except:
            img = None
    if img:
        if await delete_image(message.chat.id, img):
            await message.answer(f"{img} deleted, bye bye")
        else:
            await message.answer(f'idk what {img} is')
    else:
        await message.answer("???")


@dp.message(Command("Asa_delete_all_messages"))
async def asa_delete_all_messages(message: types.Message):
    if str(message.from_user.id) == OWNER:
        await post_femcel(message, 1)
        await delete_all_messages(message.chat.id)
        await message.answer("Bam!")
    else:
        await message.answer("No way")


@dp.message(Command("Asa_delete_all_images"))
async def asa_delete_all_images(message: types.Message):
    if str(message.from_user.id) == OWNER:
        await post_femcel(message, 1)
        await delete_all_images(message.chat.id)
        await message.answer("Bam!")
    else:
        await message.answer("No way")


@dp.message(F.text)
async def echo_handler(message: types.Message) -> None:
    text = message.text.lower()
    await insert_message(message.chat.id, text)
    if re.search(r"\b(?:f+e+m+?.?c+e+l+\w*|ф+е+м+?.?ц+е+л+\w*|a+s+a+?.?|а+с+?.?|а+с+а+|m+i+t+a+k+?.?|м+и+т+а+к+?.?)\b",
                 text):
        await insert_message(message.chat.id, text)
        await post_femcel(message, 1)
        await post_random(message, CHANCE)
        return
    for response, pattern in triggers.items():
        if re.search(pattern, text):
            await message.answer(response)
            break
    await post_random(message, CHANCE)
    await say_stuff(message, CHANCE_SAY)
    await post_femcel(message, CHANCE_STICKER)


@dp.message(F.photo)
async def echo_photo(message: types.Message) -> None:
    text = ""
    await insert_image(message.chat.id, message.photo[-1].file_id)
    try:
        text = message.text
    except:
        pass
    try:
        text = message.caption
    except:
        pass
    if text: await insert_message(message.chat.id, text.lower())
    await post_random(message, CHANCE)
    await say_stuff(message, CHANCE_SAY)
    await post_femcel(message, CHANCE_STICKER)


@dp.message(F.sticker)
async def echo_sticker(message: types.Message) -> None:
    await message.send_copy(chat_id=message.chat.id)
    await post_random(message, CHANCE)
    await say_stuff(message, CHANCE_SAY)
    await post_femcel(message, CHANCE_STICKER)


@dp.message(~F.text & ~F.photo & ~F.sticker)
async def echo_any(message: types.Message):
    text = ""
    try:
        text = message.text
    except:
        pass
    try:
        text = message.caption
    except:
        pass
    if text: await insert_message(message.chat.id, text.lower())
    await post_random(message, CHANCE)
    await say_stuff(message, CHANCE_SAY)
    await post_femcel(message, CHANCE_STICKER)


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
