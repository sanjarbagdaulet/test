import asyncio
from typing import Optional

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from config import API_TOKEN

loop = asyncio.get_event_loop()

bot = Bot(token=API_TOKEN, loop=loop)

bot = Bot(token=API_TOKEN, loop=loop)
# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
	await message.reply(message.chat.first_name)

if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)