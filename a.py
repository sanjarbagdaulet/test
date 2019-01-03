import asyncio
from typing import Optional
import sqlite3
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

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

conn = sqlite3.connect('db.db')
c = conn.cursor()

# States
class Form(StatesGroup):
	started = State()
	region = State()
	agency = State()
	content = State()
	casenum = State()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
	markup.add("Құжатты тіркеу", "Басқа")
	markup.add("Басқа", "Басқа")

	await message.reply("Әрекетті таңдаңыз:", reply_markup=markup)
	await Form.started.set()

@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(lambda message: message.text.lower() == 'cancel', state='*')
async def cancel_handler(message: types.Message, state: FSMContext, raw_state: Optional[str] = None):
    """
    Allow user to cancel any action
    """
    if raw_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()

@dp.message_handler(lambda message: message.text not in ["Құжатты тіркеу", "Басқа", "Басқа", "Басқа"], state=Form.started)
async def failed_process_act(message: types.Message):
	return await message.reply("Мұндай әрекет табылмады. Тек төмендегі әрекеттердің бірін таңдаңыз:")


@dp.message_handler(state=Form.started)
async def process_act(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['regdoc'] = message.text

	markup = types.ReplyKeyboardRemove()
	await Form.next()
	await message.reply("Сіз құжатты тіркеу әрекетін таңдадыңыз. Ең алдымен құжаттың қай аймаққа жолданатынын жазыңыз:", reply_markup=markup)

@dp.message_handler(state=Form.region)
async def process_region(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['region'] = message.text

	await Form.next()
	await message.reply("Құжат " + data['region'] + " аймағына жолданады. Енді мекемені жазыңыз:")

@dp.message_handler(state=Form.agency)
async def process_region(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['agency'] = message.text

	await Form.next()
	await message.reply("Құжат " + data['agency'] + " мекемесіне жолданады. Енді құжаттың қысқаша мазмұнын жазыңыз:")

@dp.message_handler(state=Form.content)
async def process_region(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['content'] = message.text

	await Form.next()
	await message.reply("Құжаттың қысқаша мазмұны алынды. Енді құжат қатысты істің номерін жазыңыз:")

@dp.message_handler(state=Form.casenum)
async def process_region(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['casenum'] = message.text

	c.execute("SELECT * FROM rega ORDER BY did DESC LIMIT 0,1")
	fetch = c.fetchall()

	next_did = fetch[0][0] + 1
	reger = message.chat.first_name
	region = data['region']
	agency = data['agency']
	content = data['content']
	casenum = data['casenum']

	await bot.send_message(message.chat.id, md.text(
		md.text('Сонымен, ', md.bold(data['regdoc']), " әрекеті таңдалды"),
		md.text('Құжаттың шығыс тіркеу номері: ', next_did),
		md.text('Құжатты тіркеген: ', reger),
		md.text('Құжат жолданатын аймақ: ', region),
		md.text('Құжат жолданатын мекеме: ', agency),
		md.text('Құжаттың қысқаша мазмұны: ', content),
		md.text('Құжат қатысты істің номері: ', casenum),
		sep='\n\n'), parse_mode=ParseMode.MARKDOWN)

	c.execute("INSERT INTO rega(did,reger,region,agency,content,casenum) VALUES(?,?,?,?,?,?)", (next_did, reger, region, agency, content, casenum))
	conn.commit()

	# Finish conversation
	data.state = None
	await state.finish()
	
if __name__ == '__main__':
	executor.start_polling(dp, loop=loop, skip_updates=True)
