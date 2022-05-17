from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher, Bot, types, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import datetime
import shif
import os
import json
import configparser
import requests
import function_db
import keyboard


config = configparser.ConfigParser()
config.read("settings.ini")
tokenBot = config["bot"]["bot_token"]
hostIP = config["host"]["host_ip"]
TypeOfControl = int(config["robot"]["control"])


bot = Bot(token=tokenBot)
dp = Dispatcher(bot, storage=MemoryStorage())


class Register(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_email = State()
    waiting_for_adres = State()


class NewOrder(StatesGroup):
    waiting_for_item = State()
    waiting_for_pay = State()


menu_btn = ['Меню', 'Настройка']
product_btn = ['Пицца', 'Мороженное']


def keyboards_create(ListNameBTN, NumberColumns=2):
    keyboards = types.ReplyKeyboardMarkup(row_width=NumberColumns, resize_keyboard=True)
    btn_names = [types.KeyboardButton(text=x) for x in ListNameBTN]
    keyboards.add(*btn_names)
    return keyboards


def crypto_decode(message, code_list):
    hesh = str(db.check_active_order(message)[0]) 
    hesh = json.loads(hesh)
    decode_sql = bytes.decode(shif.decrypt(enc_dict=hesh, password=code_list[1]))
    return decode_sql


def requestAPI_QR(hostIP, decode, user_id):
    res = requests.get(f'http://{hostIP}/qr_code?code={decode}&user={user_id}')
    return res.json()['user']


def requestAPI_DRIVE(hostIP, command):
    requests.get(f'http://{hostIP}/{command}')


""" тестовая функция управления по API посредством клавиатуры"""
def robotRUNmanual(hostIP, decode_sql, user_id):
    print('Управление включено!')
    keyboard.add_hotkey('enter', lambda: requestAPI_DRIVE(hostIP, 'stop')) 
    keyboard.add_hotkey('tab', lambda: requestAPI_DRIVE(hostIP, 'stop'))  
    keyboard.add_hotkey('up', lambda: requestAPI_DRIVE(hostIP, 'forward'))
    keyboard.add_hotkey('right', lambda: requestAPI_DRIVE(hostIP, 'turnRight'))  
    keyboard.add_hotkey('left', lambda: requestAPI_DRIVE(hostIP, 'turnLeft'))
    keyboard.add_hotkey('down', lambda: requestAPI_DRIVE(hostIP, 'backward'))       
    keyboard.wait('esc')
    print('Начинаю обработку кода...')
    request = requestAPI_QR(hostIP, decode_sql, user_id)
    db.update_status(request)
    print('Заказ получен!')


""" вариант автоматического управления по API (нужна функция - передатчик (Работает Роман)"""
def robotRUNauto(hostIP, decode_sql, user_id):
    while True:
        message = input('Введите команду:') # тут будет фукнция ромы каждый раз давать значения
        if message == 'esc':
            break
        else:
            requestAPI_DRIVE(hostIP, message)
    print('Начинаю обработку кода...')
    request = requestAPI_QR(hostIP, decode_sql, user_id)
    db.update_status(request)
    print('Заказ получен!')


@dp.message_handler()
async def start_message(message : types.Message):
    if db.check_in_db(message) is None:
        await message.answer('Для заказа нужно пройти регистрацию!')
        await message.answer('Как к вам обращаться ?')
        await Register.waiting_for_name.set()
    else:
        if message.text == 'Меню' or message.text == '/start':
            await message.answer('Добро пожаловать в меню:', reply_markup=keyboards_create(product_btn))
            await NewOrder.waiting_for_item.set()
        elif message.text =="Настройка":
            await message.answer('Настройки профиля')
        else:
            await message.answer('Не знаю такой команды!')


@dp.message_handler(state=Register.waiting_for_name)
async def napravlenie(message: types.Message, state: FSMContext):
    await state.update_data(name = message.text)
    await message.answer('Ваш номер телефона ?')
    await Register.next()


@dp.message_handler(state=Register.waiting_for_phone)
async def napravlenie(message: types.Message, state: FSMContext):
    await state.update_data(phone = message.text)
    await message.answer('Ваша электронная почта?')
    await Register.next()  


@dp.message_handler(state=Register.waiting_for_email)
async def napravlenie(message: types.Message, state: FSMContext):
    await state.update_data(email = message.text)
    await message.answer('Адресс доставки:')
    await Register.next()  


@dp.message_handler(state=Register.waiting_for_adres)
async def napravlenie(message: types.Message, state: FSMContext):
    await state.update_data(adress = message.text)
    user_data = await state.get_data()
    name = user_data['name']
    phone = user_data['phone']
    email = user_data['email']
    adress = user_data['adress']
    user_info = [message.from_user.id, name, phone, email, adress]
    db.register_new_user(user_info)
    await message.answer('Спасибо за регистрацию!', reply_markup=keyboards_create(menu_btn))
    await state.finish() 


@dp.message_handler(state=NewOrder.waiting_for_item)
async def napravlenie(message: types.Message, state: FSMContext):
    if db.check_active_order(message) is not None:
        await message.answer('У вас есть активный заказ! Дождитетесь его!\nПожалейте наших роботов')
    else:
        await state.update_data(item = message.text)
        user_data = await state.get_data()
        item = user_data['item']
        user_id = message.from_user.id
        code = shif.crypto(message)
        date = datetime.date.today() 
        order_info = [code[0], date, 0, user_id, item]
        db.create_new_order(order_info)
        await state.finish()
    
        photo = open(f'img/{user_id}.png', 'rb')
        await bot.send_photo(user_id, photo)
        os.remove(f'img/{user_id}.png')
    
        """тут идет функция движения, в нее передается запрос (после окончания движения)"""
        decode_sql = crypto_decode(message, code)
        if TypeOfControl == 0:
            robotRUNmanual(hostIP, decode_sql, user_id)
        else:
            robotRUNauto(hostIP, decode_sql, user_id)
 

if __name__ == '__main__':
    db = function_db.DataBase()
    executor.start_polling(dp, skip_updates=True)