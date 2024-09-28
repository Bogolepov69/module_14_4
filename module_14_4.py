from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from homework.module14.crud_functions import get_all_products, initiate_db

initiate_db()

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())
kb = InlineKeyboardMarkup()
button1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчета', callback_data='formulas')
button3 = InlineKeyboardButton(text='Купить', callback_data='product_list')
kb.add(button1)
kb.add(button2)
kb.add(button3)

product_images = {
    1: "photo1.jpeg", 2: "photo2.jpeg",
    3: "photo3.jpeg", 4: "photo4.jpeg"
}

product_kb = InlineKeyboardMarkup()
for i in range(1, 5):
    product_kb.add(InlineKeyboardButton(text=f'Product{i}', callback_data=f'product_{i}', photo=product_images[i]))


class UserState(StatesGroup):
    age = State()
    height = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Нажмите 'Рассчитать' для начала.", reply_markup=kb)


@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer("Формула для расчета нормы калорий: 66 + 13.75 * вес + 5 * рост - 6.75 * возраст.")
    await call.answer()


@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await UserState.age.set()
    await call.message.answer("Введите ваш возраст:")


@dp.message_handler(state=UserState.age)
async def set_height(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))
    await UserState.height.set()
    await message.answer("Введите свой рост в см:")


@dp.message_handler(state=UserState.height)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(height=int(message.text))
    await UserState.weight.set()
    await message.answer("Введите свой вес в кг:")


@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    data = await state.get_data()
    age = data.get('age')
    height = data.get('height')
    weight = int(message.text)
    calories = 66 + (13.75 * weight) + (5 * height) - (6.75 * age)
    await message.answer(f"Ваша норма калорий: {calories:.2f} ккал.", reply_markup=kb)
    await state.finish()


@dp.callback_query_handler(lambda call: call.data == 'product_list')
async def get_buying_list(call: types.CallbackQuery):
    products = get_all_products()
    product_kb = InlineKeyboardMarkup()
    for product in products:
        product_kb.add(InlineKeyboardButton(text=product[1], callback_data=f'Product_{product[0]}'))
    await call.message.answer("Выберите продукт для покупки:", reply_markup=product_kb)


@dp.callback_query_handler(lambda call: call.data.startswith('product'))
async def send_confirm_message(call: types.CallbackQuery):
    product_num = int(call.data.split('_')[1])
    await call.message.answer(f"Вы успешно приобрели Product{product_num}!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)