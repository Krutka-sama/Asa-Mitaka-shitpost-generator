import asyncio
import logging
import sys
import re
from random import random, shuffle, choice
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
# from aiogram.types import FSInputFile
from decouple import config
from aiogram import Bot, Dispatcher, types, F
from database import create_table, connect, close, insert_message, insert_image, get_random_text, get_random_image, \
    delete_message, delete_image, delete_all_messages, delete_all_images, get_banned, ban, unban
from shitpost import shitpost
from stuff import *
from exeption import Banned
from functools import wraps

# from aiogram.client.session.aiohttp import AiohttpSession
# PROXY_URL = "http://proxy.server:3128"

TOKEN = config('BOT_TOKEN')
NAME = config('DB_NAME')
OWNER = int(config('OWNER_ID'))
SIZE_LAT = int(config('DEFAULT_SIZE_LAT'))
CHANCE = float(config('DEFAULT_CHANCE'))
CHANCE_SKIP = float(config('DEFAULT_CHANCE_SKIP_WORD'))
CHANCE_STICKER = float(config('DEFAULT_CHANCE_STICKER'))
CHANCE_SAY = float(config('DEFAULT_CHANCE_SAY'))

BLACK_LIST: list[int] = []

dp = Dispatcher()


# DEFAULT_SETTINGS = {"id": None, "SIZE_LAT": SIZE_LAT, "CHANCE": CHANCE,
#                     "CHANCE_SKIP": CHANCE_SKIP,
#                     "CHANCE_STICKER": CHANCE_STICKER, "CHANCE_SAY": CHANCE_SAY}


@dp.startup()
async def on_startup():
    await bot.send_message(chat_id=OWNER, text="Hii im back")

    await bot.send_message(chat_id=-1002009922325, text="Hii im back")


@dp.shutdown()
async def on_shutdown():
    await bot.send_message(chat_id=OWNER, text="Hii im back")

    await bot.send_message(chat_id=-1002009922325, text="Im outta here")

    await close()


def black_list(message: types.Message):
    if message.chat.id in BLACK_LIST or message.from_user.id in BLACK_LIST:
        raise Banned


def blacklist_check(func):
    @wraps(func)
    async def wrapper(message):
        try:
            black_list(message)
        except Banned:
            return
        return await func(message)

    return wrapper


async def say_stuff(message: types.Message, chance: float):
    if random() <= chance:
        text = await get_random_text(message.chat.id)
        if not text:
            await message.answer("Fuck you")
            return
        text = text.split(" ")
        if len(text) == 1:
            await message.answer(text[0].capitalize())
            return
        shuffle(text)
        answer = ""
        for i in text:
            if random() <= CHANCE_SKIP:
                continue
            answer += " "
            answer += i
        if answer:
            await message.answer(answer.capitalize())
        else:
            await post_femcel(message, 1)


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


@dp.message(Command("Asa_help"))
@blacklist_check
async def command_start_handler(message: types.Message):
    await message.answer(f"Hi, {message.from_user.full_name}, Im Asa Mitaka. Im autistic and I love shitposting!\n\n"
                         f"Use /Asa_shitpost to create a shitpost from last random 100 messages and pics,"
                         f" you can also send me a pic directly or reply to one with the same command"
                         f" to create post with the pic you want, it works with text too!\n\n"
                         f"Use /Asa_delete_message and /Asa_delete_image"
                         f" to get rid of unwanted pictures and signatures!\n\n"
                         f"I work only with latin and cyrillic characters!!! And i wont display emoji!!!")


@dp.message(Command("Asa_shitpost"))
@blacklist_check
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
@blacklist_check
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
@blacklist_check
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
    if message.from_user.id == OWNER:
        await post_femcel(message, 1)
        await delete_all_messages(message.chat.id)
        await message.answer("Bam!")
    else:
        await message.answer("No way")


@dp.message(Command("Asa_delete_all_images"))
async def asa_delete_all_images(message: types.Message):
    if message.from_user.id == OWNER:
        await post_femcel(message, 1)
        await delete_all_images(message.chat.id)
        await message.answer("Bam!")
    else:
        await message.answer("No way")


@dp.message(Command("Asa_ban"))
async def asa_ban(message: types.Message):
    global BLACK_LIST
    if message.from_user.id == OWNER:
        chat_id = message.text[9::]
        if not chat_id:
            try:
                chat_id = message.reply_to_message.from_user.id
            except:
                chat_id = message.chat.id
        await ban(chat_id)
        BLACK_LIST = await get_banned()
        await message.answer("Frick you")
    else:
        await message.answer("No way")


@dp.message(Command("Asa_unban"))
async def asa_unban(message: types.Message):
    global BLACK_LIST
    if message.from_user.id == OWNER:
        chat_id = message.text[11::]
        if not chat_id:
            try:
                chat_id = message.reply_to_message.from_user.id
            except:
                chat_id = message.chat.id
        if chat_id in BLACK_LIST:
            await unban(chat_id)
            BLACK_LIST = await get_banned()
            await message.answer("Hii")
        else:
            await message.answer("???")
    else:
        await message.answer("No way")


@dp.message(F.text)
@blacklist_check
async def echo_handler(message: types.Message) -> None:
    text = message.text.lower()
    await insert_message(message.chat.id, text)
    if re.search(r"\b(?:f+e+m+?.?c+e+l+\w*|ф+е+м+?.?ц+е+л+\w*|a+s+a+?.?|а+с+?.?|а+с+а+|m+i+t+a+k+?.?|м+и+т+а+к+?.?)\b",
                 text):
        #await insert_message(message.chat.id, text)
        #await post_femcel(message, 1)
        #await post_random(message, CHANCE)
        #return

        if random() <= 0.9:
            print("here")
            await post_femcel(message, 1)
            await post_random(message, CHANCE)
            return
        else:
            await say_stuff(message, 1)
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
@blacklist_check
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
@blacklist_check
async def echo_sticker(message: types.Message) -> None:
    await message.send_copy(chat_id=message.chat.id)
    await post_random(message, CHANCE)
    await say_stuff(message, CHANCE_SAY)
    await post_femcel(message, CHANCE_STICKER)


@dp.message(~F.text & ~F.photo & ~F.sticker)
@blacklist_check
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
    global bot, BLACK_LIST
    bot = Bot(TOKEN)

    # session = AiohttpSession(proxy=PROXY_URL)
    # bot = Bot(TOKEN, session=session)

    await connect(NAME)
    await create_table()
    BLACK_LIST = await get_banned()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
