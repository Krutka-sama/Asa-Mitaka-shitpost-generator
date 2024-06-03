import asyncio
import logging
import sys
import re
from random import random, choice
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile
from decouple import config
from aiogram import Bot, Dispatcher, types, F
from database import create_table, connect, close, insert_message, insert_image, get_random_text, get_random_image, \
    delete_message, delete_image, delete_all_messages, delete_all_images, get_banned, ban, unban, get_all_settings, \
    delete_settings, set_settings, get_ai_users, add_ai_user, remove_ai_user, M_SCOPE, I_SCOPE
from shitpost import shitpost
from stuff import *
from exeption import Banned
from functools import wraps
from characterai import aiocai

TOKEN = config('BOT_TOKEN')
NAME = config('DB_NAME')
OWNER = int(config('OWNER_ID'))
SIZE_LAT = int(config('DEFAULT_SIZE_LAT'))
CHANCE = float(config('DEFAULT_CHANCE'))
CHANCE_STICKER = float(config('DEFAULT_CHANCE_STICKER'))

asa = config('ASA_AI')
client = aiocai.Client(config('TOKEN_AI'))

BLACK_LIST: list[int] = []
SETTINGS = {0: [SIZE_LAT, CHANCE, CHANCE_STICKER]}
AI_USERS = {}
dp = Dispatcher()


@dp.shutdown()
async def on_shutdown(): await close()


async def validate_settings(message: types.Message) -> list | None:
    s = message.text.split(maxsplit=1)[1]
    try:
        s = list(map(float, s.split(" ")))
    except ValueError:
        await message.answer("Bruh")
        return
    if len(s) != 3:
        await message.answer("Invalid settings, moron")
        return

    s[0] = int(s[0])
    s[1] = round(s[1], 2)
    s[2] = round(s[2], 2)

    SIZE_LAT = s[0]
    CHANCE = s[1]
    CHANCE_STICKER = s[2]

    if SIZE_LAT > 100 or SIZE_LAT < 10:
        await message.answer("Invalid size")
        return

    if CHANCE > 0.8 or CHANCE < 0:
        await message.answer("Invalid chance to shitpost")
        return

    if CHANCE_STICKER > 0.8 or CHANCE_STICKER < 0:
        await message.answer("Invalid chance to send sticker")
        return
    return s


def format_settings(s: list) -> str:
    return (f"Latin text size {s[0]}\n"
            f"Chance to post {s[1]}\n"
            f"Chance to send sticker {s[2]}\n")


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


async def post_random(message: types.Message, chance: float):
    if random() <= chance:
        file_id = await get_random_image(message.chat.id)
        text = await get_random_text(message.chat.id)
        if not file_id or not text:
            await message.answer("Dumbass")
            return
        file_info = await bot.get_file(file_id)
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


async def ai_response(user_message: str, chat_id: int):
    async with await client.connect() as chat:
        response = await chat.send_message(asa, AI_USERS[chat_id], user_message)
        return response.text


@dp.message(CommandStart())
@blacklist_check
async def command_start_handler(message: types.Message):
    await message.answer(f"Hi, {message.from_user.full_name}, Im Asa Mitaka. Im autistic and I love shitposting!\n\n"
                         f"Use /asa_shitpost to create a shitpost from last random {M_SCOPE} messages and {I_SCOPE} pics,"
                         f" you can also send me a pic directly or reply to one with the same command"
                         f" to create post with the pic you want, it works with text too!\n\n"
                         f"Use /asa_delete_message and /asa_delete_image"
                         f" to get rid of unwanted pictures and signatures!\n\n"
                         f"Use /asa to chat\n"
                         f"Use /asa_forget to start a new chat with me\n\n"
                         f"Use /asa_settings to check your current settings\n"
                         f"Use /asa_set_default to return to default settings\n"
                         f"Use /asa_set_settings to change settings, use the example:\n"
                         f"/asa_set_settings 60 0.1 0.05\n"
                         f"This will make latin text size 60, chance to post 10%, chance to send sticker 5%\n"
                         f"You must provide 3 numbers and:\n"
                         f"Text size must in (10;100)\n"
                         f"Post chance in [0.0;0.8]\n"
                         f"Sticker chance in [0.0;0.8]\n\n"
                         f"I work only with latin and cyrillic characters!!! And i wont display emoji!!!\n\n"
                         f"By continuing using me you agree that you are fine that your privacy depends on online hosting Im currently using")


@dp.message(Command("asa"))
@blacklist_check
async def handle_ai_request(message):
    global AI_USERS
    if not (message.chat.id in AI_USERS):
        me = await client.get_me()
        async with await client.connect() as chat:
            new, answer = await chat.new_chat(asa, me.id)
            await add_ai_user(message.chat.id, new.chat_id)
            AI_USERS = await get_ai_users()
    if message.reply_to_message:
        user = message.reply_to_message.from_user.full_name
        try:
            user_message = message.reply_to_message.text
        except:
            try:
                user_message = message.reply_to_message.caption
            except:
                user_message = None
    else:
        user = message.from_user.full_name
        try:
            user_message = message.caption.split(maxsplit=1)[1]
        except:
            try:
                user_message = message.text.split(maxsplit=1)[1]
            except:
                user_message = None
    if user_message:
        m = user + ": " + user_message
    else:
        m = ""
    response_text = await ai_response(m, message.chat.id)
    await message.answer(response_text)


@dp.message(Command("asa_forget"))
@blacklist_check
async def asa_forget(message: types.Message):
    global AI_USERS
    if message.from_user.id == OWNER:
        try:
            chat_id = int(message.text.split(maxsplit=1)[1])
        except:
            try:
                chat_id = message.reply_to_message.from_user.id
            except:
                chat_id = message.chat.id
    else:
        chat_id = message.chat.id

    await remove_ai_user(chat_id)
    AI_USERS = await get_ai_users()
    await message.answer(f"Uhh whos {chat_id} again?")


@dp.message(Command("asa_id"))
@blacklist_check
async def asa_get_id(message: types.Message):
    if message.from_user.id == OWNER:
        try:
            chat_id = int(message.text.split(maxsplit=1)[1])
        except:
            try:
                chat_id = message.reply_to_message.from_user.id
            except:
                chat_id = message.chat.id
        await message.answer(f"{chat_id}")


@dp.message(Command("asa_shitpost"))
@blacklist_check
async def asa_shitpost(message: types.Message):
    if message.reply_to_message:
        try:
            img = message.reply_to_message.photo[-1].file_id
        except:
            img = await get_random_image(message.chat.id)
        try:
            text = message.text.split(maxsplit=1)[1]
        except:
            try:
                text = message.reply_to_message.text
            except:
                try:
                    text = message.reply_to_message.caption
                except:
                    text = await get_random_text(message.chat.id)
    else:
        try:
            img = message.photo[-1].file_id
        except:
            img = await get_random_image(message.chat.id)
        try:
            text = message.caption.split(maxsplit=1)[1]
        except:
            try:
                text = message.text.split(maxsplit=1)[1]
            except:
                text = await get_random_text(message.chat.id)
    print(text)
    if not text or not img:
        await message.answer("Nah")
        return
    file_info = await bot.get_file(img)
    image_data = await bot.download_file(file_info.file_path)
    modified_image_buffer = await shitpost(text, image_data, SETTINGS.get(message.chat.id, SETTINGS.get(0))[0])
    img = BufferedInputFile(modified_image_buffer.getvalue(), "shitpost")
    await message.answer_photo(img)
    modified_image_buffer.truncate(0)


@dp.message(Command("asa_delete_message"))
@blacklist_check
async def asa_delete_message(message: types.Message):
    if message.reply_to_message:
        try:
            text = message.text.split(maxsplit=1)[1]
        except:
            text = message.reply_to_message.text
            if not text:
                text = message.reply_to_message.caption
                if not text:
                    text = None
    else:
        try:
            text = message.caption.split(maxsplit=1)[1]
        except:
            try:
                text = message.text.split(maxsplit=1)[1]
            except:
                text = None
    if text:
        if await delete_message(message.chat.id, text):
            await message.answer(f'"{text}" deleted, bye bye')
        else:
            await message.answer(f'idk what "{text}" is')
    else:
        await message.answer("???")


@dp.message(Command("asa_delete_image"))
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


@dp.message(Command("asa_delete_all_messages"))
async def asa_delete_all_messages(message: types.Message):
    if message.from_user.id == OWNER:
        await post_femcel(message, 1)
        await delete_all_messages(message.chat.id)
        await message.answer("Bam!")
    else:
        await message.answer("No way")


@dp.message(Command("asa_delete_all_images"))
async def asa_delete_all_images(message: types.Message):
    if message.from_user.id == OWNER:
        await post_femcel(message, 1)
        await delete_all_images(message.chat.id)
        await message.answer("Bam!")
    else:
        await message.answer("No way")


@dp.message(Command("asa_ban"))
async def asa_ban(message: types.Message):
    global BLACK_LIST
    if message.from_user.id == OWNER:
        try:
            chat_id = int(message.text.split(maxsplit=1)[1])
        except:
            try:
                chat_id = message.reply_to_message.from_user.id
            except:
                chat_id = message.chat.id
        await ban(chat_id)
        BLACK_LIST = await get_banned()
        await message.answer(f"Frick you, {chat_id}")
    else:
        await message.answer(f"No way")


@dp.message(Command("asa_unban"))
async def asa_unban(message: types.Message):
    global BLACK_LIST
    if message.from_user.id == OWNER:
        try:
            chat_id = int(message.text.split(maxsplit=1)[1])
        except:
            try:
                chat_id = message.reply_to_message.from_user.id
            except:
                chat_id = message.chat.id
        if chat_id in BLACK_LIST:
            await unban(chat_id)
            BLACK_LIST = await get_banned()
            await message.answer(f"Hii, {chat_id}")
        else:
            await message.answer("???")
    else:
        await message.answer("No way")


@dp.message(Command("asa_settings"))
@blacklist_check
async def asa_settings(message: types.Message):
    await message.answer(
        f"Current settings for {message.chat.id}:\n" + format_settings(SETTINGS.get(message.chat.id, SETTINGS.get(0))))


@dp.message(Command("asa_set_settings"))
@blacklist_check
async def asa_set_settings(message: types.Message):
    settings = await validate_settings(message)
    if settings:
        SETTINGS[message.chat.id] = settings
        await set_settings(message.chat.id, settings)
        await asa_settings(message)
    else:
        return


@dp.message(Command("asa_set_default"))
@blacklist_check
async def asa_set_default(message: types.Message):
    try:
        SETTINGS.pop(message.chat.id)
        await delete_settings(message.chat.id)
        await asa_settings(message)
    except KeyError:
        await message.answer("Your settings are default, idiot")


@dp.message(Command("asa_leave"))
@blacklist_check
async def asa_leave(message: types.Message):
    if message.from_user.id == OWNER:
        try:
            chat_id = message.text.split(maxsplit=1)[1]
        except:
            chat_id = message.chat.id
        try:
            await message.answer("Bye losers")
            await bot.leave_chat(chat_id)
        except:
            await message.answer("...wait a minute")
    else:
        await message.answer("No way")


@dp.message(F.text)
@blacklist_check
async def echo_handler(message: types.Message) -> None:
    text = message.text.lower()
    await insert_message(message.chat.id, text)
    if re.search(r"\b(?:f+e+m+?.?c+e+l+\w*|ф+е+м+?.?ц+е+л+\w*|a+s+a+?.?|а+с+?.?|а+с+а+|m+i+t+a+k+?.?|м+и+т+а+к+?.?)\b",
                 text):
        await post_femcel(message, 1)
        await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
        return

    for response, pattern in triggers.items():
        if re.search(pattern, text):
            await message.answer(response)
            break

    await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
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
    await post_femcel(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[2])


@dp.message(F.sticker)
@blacklist_check
async def echo_sticker(message: types.Message) -> None:
    await message.send_copy(chat_id=message.chat.id)
    await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
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
            await post_femcel(message, 1)
            await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
            return

        for response, pattern in triggers.items():
            if re.search(pattern, text):
                await message.answer(response)
                break

    await post_random(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[1])
    await post_femcel(message, SETTINGS.get(message.chat.id, SETTINGS.get(0))[2])


async def main() -> None:
    global bot, BLACK_LIST, SETTINGS, AI_USERS
    bot = Bot(TOKEN)
    await connect(NAME)
    await create_table()
    BLACK_LIST = await get_banned()
    SETTINGS |= await get_all_settings()
    AI_USERS = await get_ai_users()
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
