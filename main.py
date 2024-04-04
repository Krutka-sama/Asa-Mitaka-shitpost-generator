import asyncio
import logging
import sys
import re
import random
from decouple import config
from aiogram import Bot, Dispatcher, Router, types, F
# Bot token can be obtained via https://t.me/BotFather
TOKEN = config('BOT_TOKEN')

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()

triggers = {
    'ТРАХ': r"\b\w*трах\w*\b",
    'ГОВНО': r"\b\w+(?:core|кор)\b",
    'Планета ТРАХА': r"(?:планет[аеыуо]?\s?техно|пт)\b"

}
# db={}
# c=5
# c1=10

@dp.message(F.text)
async def echo_handler(message: types.Message) -> None:
    text = message.text.lower()
    for response, pattern in triggers.items():
        if re.search(pattern, text):
            await message.answer(text=response)
            break
    # rng = random.SystemRandom()
    # num = rng.randrange(8, 20)
    # print(db)
    # print(num)
    # if num > c1 and str(message.chat.id) in db:
    #     await message.answer_photo(photo=db[str(message.chat.id)])
        # else:
        #     await message.send_copy(chat_id=message.chat.id)
        #     break

# @dp.message(F.photo)
# async def echo_photo(message: types.Message) -> None:
#     rng = random.SystemRandom()
#     num = rng.randrange(1,10)
#     print(num)
#     if num <= c:
#         db[str(message.chat.id)]=message.photo[-1].file_id

@dp.message(F.sticker)
async def echo_sticker(message: types.Message) -> None:
    await message.send_copy(chat_id=message.chat.id)

async def main() -> None:
    bot = Bot(TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())