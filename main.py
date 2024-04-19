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
    delete_message, delete_image, delete_all_messages, delete_all_images, get_banned, ban, unban, get_all_settings, \
    delete_settings, set_settings, get_chat_ids
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
CHANCE_STICKER = float(config('DEFAULT_CHANCE_STICKER'))
CHANCE_SAY = float(config('DEFAULT_CHANCE_SAY'))
CHANCE_SKIP = float(config('DEFAULT_CHANCE_SKIP_WORD'))

BLACK_LIST: list[int] = []
SETTINGS = {0: [SIZE_LAT, CHANCE, CHANCE_STICKER,
                CHANCE_SAY, CHANCE_SKIP]}

dp = Dispatcher()


@dp.startup()
async def on_startup():
    ids = await get_chat_ids()
    for chat_id in ids:
        try:
            await bot.send_message(chat_id=chat_id, text="Hii im back")
        except:
            pass


@dp.shutdown()
async def on_shutdown():
    ids = await get_chat_ids()
    for chat_id in ids:
        try:
            await bot.send_message(chat_id=chat_id, text="Im outta here")
        except:
            pass
    await close()


async def validate_settings(message: types.Message) -> list | None:
    s = message.text
    try:
        s = list(map(float, s[18::].split(" ")))
    except ValueError:
        await message.answer("Bruh")
        return
    if len(s) != 5:
        await message.answer("Invalid settings, moron")
        return

    s[0] = int(s[0])
    s[1] = round(s[1], 2)
    s[2] = round(s[2], 2)
    s[3] = round(s[3], 2)
    s[4] = round(s[4], 2)

    SIZE_LAT = s[0]
    CHANCE = s[1]
    CHANCE_STICKER = s[2]
    CHANCE_SAY = s[3]
    CHANCE_SKIP = s[4]

    if SIZE_LAT > 100 or SIZE_LAT < 10:
        await message.answer("Invalid size")
        return

    if CHANCE > 0.8 or CHANCE < 0:
        await message.answer("Invalid chance to shitpost")
        return

    if CHANCE_STICKER > 0.8 or CHANCE_STICKER < 0:
        await message.answer("Invalid chance to send sticker")
        return

    if CHANCE_SAY > 0.5 or CHANCE_SAY < 0:
        await message.answer("Invalid chance to say something")
        return

    if CHANCE_SKIP > 1 or CHANCE_SKIP < 0:
        await message.answer("Invalid chance to skip word")
        return
    return s


def format_settings(s: list) -> str:
    return (f"Latin text size {s[0]}\n"
            f"Chance to post {s[1]}\n"
            f"Chance to send sticker {s[2]}\n"
            f"Chance to say something {s[3]}\n"
            f"Chance to skip word when saying something {s[4]}")


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
        text2 = await get_random_text(message.chat.id)
        if not text:
            await message.answer("Fuck you")
            return
        text = text.split(" ") + text2.split(" ")
        shuffle(text)
        answer = ""
        for i in text:
            if random() <= SETTINGS.get(message.chat.id, SETTINGS.get(0))[4]:
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
        modified_image_buffer = await shitpost(text, image_data, SETTINGS.get(message.chat.id, SETTINGS.get(0))[0])
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
                         f" to get rid of unwanted pictures and signatures!\n"
                         f"Use /Asa_say to say something\n\n"
                         f"Use /Asa_settings to check your current settings\n"
                         f"Use /Asa_set_default to return to default settings\n"
                         f"Use /Asa_set_settings to change settings, use the example:\n"
                         f"/Asa_set_settings 60 0.1 0.05 0.01 0.4\n"
                         f"This will make latin text size 60, chance to post 10%, chance to send sticker 5%, "
                         f"chance to say something 1% and chance to skip word when saying something 40%\n"
                         f"You must provide 5 numbers and:\n"
                         f"Text size must in (10;100)\n"
                         f"Post chance in [0.0;0.8]\n"
                         f"Sticker chance in [0.0;0.8]\n"
                         f"Say chance in [0.0;0.5]\n"
                         f"Skip chance in [0.0;1.0]\n\n"
                         f"I work only with latin and cyrillic characters!!! And i wont display emoji!!!\n\n"
                         f"I (currently) dont encrypt your data so copy&modify me and host by yourself if you care about your privacy!!!\n"
                         f"If you need any help or have a suggestion dm my creator @krutka_sama")


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
    modified_image_buffer = await shitpost(text, image_data, SETTINGS.get(message.chat.id, SETTINGS.get(0))[0])
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


@dp.message(Command("Asa_settings"))
@blacklist_check
async def asa_settings(message: types.Message):
    await message.answer(
        f"Current settings for {message.chat.id}:\n" + format_settings(SETTINGS.get(message.chat.id, SETTINGS.get(0))))


@dp.message(Command("Asa_set_settings"))
@blacklist_check
async def asa_set_settings(message: types.Message):
    settings = await validate_settings(message)
    if settings:
        SETTINGS[message.chat.id] = settings
        await set_settings(message.chat.id, settings)
        await asa_settings(message)
    else:
        return


@dp.message(Command("Asa_set_default"))
@blacklist_check
async def asa_set_default(message: types.Message):
    try:
        SETTINGS.pop(message.chat.id)
        await delete_settings(message.chat.id)
        await asa_settings(message)
    except KeyError:
        await message.answer("Your settings are default, idiot")


@dp.message(Command("Asa_say"))
@blacklist_check
async def asa_say(message: types.Message):
    await say_stuff(message, 1)


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
            await post_femcel(message, 1)
            await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
            return
        else:
            await say_stuff(message, 1)
            await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
            return

    for response, pattern in triggers.items():
        if re.search(pattern, text):
            await message.answer(response)
            break
    await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])

    await say_stuff(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[3])

    await post_femcel(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[2])


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
    await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
    await say_stuff(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[3])
    await post_femcel(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[2])


@dp.message(F.sticker)
@blacklist_check
async def echo_sticker(message: types.Message) -> None:
    await message.send_copy(chat_id=message.chat.id)
    await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
    await say_stuff(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[3])
    await post_femcel(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[2])


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
    if text:
        text = text.lower()
        await insert_message(message.chat.id, text)

        if re.search(
                r"\b(?:f+e+m+?.?c+e+l+\w*|ф+е+м+?.?ц+е+л+\w*|a+s+a+?.?|а+с+?.?|а+с+а+|m+i+t+a+k+?.?|м+и+т+а+к+?.?)\b",
                text):
            # await insert_message(message.chat.id, text)
            # await post_femcel(message, 1)
            # await post_random(message, CHANCE)
            # return

            if random() <= 0.9:
                await post_femcel(message, 1)
                await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
                return
            else:
                await say_stuff(message, 1)
                await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
                return

        for response, pattern in triggers.items():
            if re.search(pattern, text):
                await message.answer(response)
                break
    await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
    await say_stuff(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[3])
    await post_femcel(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[2])


async def main() -> None:
    global bot, BLACK_LIST, SETTINGS
    bot = Bot(TOKEN)

    # session = AiohttpSession(proxy=PROXY_URL)
    # bot = Bot(TOKEN, session=session)

    await connect(NAME)
    await create_table()
    BLACK_LIST = await get_banned()
    SETTINGS |= await get_all_settings()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
