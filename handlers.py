import asyncio
import random

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove)
from aiogram.utils.callback_data import CallbackData

import sqlite3
import states
from config import admin_id
from load_all import dp, bot
from keyboard import start_menu
from inline import cancel, choice_assortment, forms_start, forms, cancel_assort, s_choice_assortment, ref_choice
from states import Forms, Ref_code


@dp.message_handler(CommandStart())
async def start_message(message: types.Message):
    user_id = message.from_user.id
    code_list = [z for z in range(1000, 10001)]
    count_ref = 0

    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS users (chat_id BIGINT, code BIGINT, count_ref TEXT)")
    db.commit()

    cur.execute("CREATE TABLE IF NOT EXISTS first_sale (chat_id BIGINT)")
    db.commit()

    cur.execute('SELECT * FROM users')
    rows = cur.fetchall()

    cur.execute(f'SELECT * FROM users WHERE chat_id = {user_id}')
    rows_user = cur.fetchall()
    if len(rows_user) == 0:
        cur.execute(f'INSERT INTO users VALUES(?,?,?)', (user_id, code_list[len(rows)], count_ref))
        db.commit()

    await message.answer('🔞 Пользоваться ботом можно ТОЛЬКО лицам старше 18 лет!\n \n'
                         '🍺 Добро пожаловать в PIVO 2 PIVO!\n \n' 
                         '✅ У нас Вы найдете лучшие сорта пива по доступным ценам\n \n'
                         '📩 Для получения дополнительной информации используйте клавиатуру бота\n \n'
                         '❗️ Чрезмерное употребление алкоголя вредит Вашему здоровью!', reply_markup=start_menu)


@dp.message_handler(Text(equals=['💵 Реф. система',' Реф. система']))
async def referals_menu(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer('У нас доступна реферальная система!\n\n'
                         'Вы можете ввести код пригласившего Вас пользователя, '
                         'чтобы получить скидку 5 % на первую покупку\n\n'
                         'Либо приглашайте других, '
                         'используя личный код. Когда 3 человека введут код и совершат покупку, '
                         'Вы получите скидку 10 %. Когда 5 человек - 15 %\n\n'
                         'Выберите действие для работы с реф. системой',
                         reply_markup=ref_choice)

@dp.callback_query_handler(text='ref_info')
async def ref_info(call: CallbackQuery):
    await call.answer(cache_time=60)
    # await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute(f'SELECT code FROM users WHERE chat_id = {call.message.chat.id}')
    code = cur.fetchone()

    cur.execute(f'SELECT count_ref FROM users WHERE code = {code[0]}')
    str_ref = cur.fetchone()
    if str_ref[0] == '0':
        count = 0
    elif str_ref[0].count(',') == 0:
        count = 1
    else:
        count = str_ref[0].count(',') + 1

    if count == 0:
        sale = 0
    elif count < 3:
        sale = 5
    elif count < 5:
        sale = 10
    else:
        count = 15

    await call.message.answer(f'Ваш личный код – {code[0]}\n'
                              f'Количество Ваших рефералов – {count}\n'
                              f'Ваша скидка - {sale} %',
                              reply_markup=cancel)


@dp.callback_query_handler(text='ref_code')
async def start_ref_code(call: CallbackQuery):
    await call.answer(cache_time=60)
    # await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Введите реферальный код')
    await Ref_code.first()


@dp.message_handler(state=Ref_code.input_code)
async def ref_code(message: types.Message, state: FSMContext):
    ref_code = str(message.text)
    id_ref = message.from_user.id

    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute(f'SELECT count_ref FROM users WHERE code = {ref_code}')
    referals = cur.fetchone()

    cur.execute(f'SELECT code FROM users WHERE chat_id = {id_ref}')
    code_main = cur.fetchone()

    cur.execute(f'SELECT chat_id FROM first_sale where chat_id = {id_ref}')
    count_fs = cur.fetchall()

    if type(referals) == tuple:
        str_referals = ''
        for i in referals:
            str_referals += str(i) + ','
        a = str_referals + str(id_ref)

        if str(id_ref) not in str_referals:
            if code_main[0] == int(ref_code):
                await message.answer('Вы ввели свой собственный код')
            elif referals[0] == '0':
                cur.execute(f'UPDATE users SET count_ref = "{id_ref}" WHERE code = "{ref_code}"')
                db.commit()
                if count_fs == 0:
                    cur.execute(f'INSERT INTO first_sale VALUES(?)', (id_ref, ))
                    db.commit()
                await message.answer('Код введён успешно. Скидка на первую покупку активирована')
            else:
                cur.execute(f'UPDATE users SET count_ref = "{a}" WHERE code = "{ref_code}"')
                db.commit()
                if count_fs == 0:
                    cur.execute(f'INSERT INTO first_sale VALUES(?)', (id_ref,))
                    db.commit()
                await message.answer('Код введён успешно. Скидка на первую покупку активирована')

        else:
            await message.answer('Вы пытаетесь ввести код повторно')
    else:
        await message.answer('Такого кода не существует')
    await state.finish()

@dp.message_handler(Text(equals=['👨‍💻 Отзывы', 'Отзывы']))
async def reviews_menu(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer('Канал с отзывами:\n'
                         'https://t.me/joinchat/LCp-jCYHBbBiZjgy', reply_markup=cancel)

@dp.message_handler(Text(equals=['☎️ Контакты', 'Контакты']))
async def contacts_menu(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer('Если есть вопросы или хотите заказать напрямую:\n'
                         '@mmmtvvv', reply_markup=cancel)

@dp.message_handler(Text(equals=['✅ Условия', 'Условия']))
async def conditions_menu(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer('✅ Огромный ассортимент и наличие!\n\n'
                         '✅ Честность и безопасность. За все время работы есть большое кол-во довольных клиентов\n\n'
                         '✅ Минимальный заказ от 5 бутылок\n\n'
                         '✅ Самовывоз в Москве\n\n'
                         '✅ Бронирование через предоплату 100%', reply_markup=cancel)

@dp.message_handler(Text(equals=['🍺 Ассортимент', 'Ассортимент']))
async def contacts_menu(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer('Выберите категорию товаров:', reply_markup=choice_assortment)


@dp.callback_query_handler(text='sigs')
async def sigs_asort(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM sigs')
    products = cur.fetchall()
    text_products = ''
    start_text = '✅ В наличии следующие позиции (цена за бутылку):\n\n'
    for i in products:
        i = [str(z) for z in i]
        str_product = ' – '.join(i)
        text_products += f"{str_product} рублей\n\n"

    await call.message.answer(text=start_text+text_products, reply_markup=cancel_assort)


@dp.callback_query_handler(text='snus')
async def snus_asort(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM snus')
    products = cur.fetchall()
    text_products = ''
    start_text = '✅ В наличии следующие позиции (цена за бутылку):\n\n'
    for i in products:
        i = [str(z) for z in i]
        str_product = ' – '.join(i)
        text_products += f"{str_product} рублей\n\n"

    await call.message.answer(text=start_text + text_products, reply_markup=cancel_assort)

@dp.callback_query_handler(text='hqd')
async def hqd_asort(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM hqd')
    products = cur.fetchall()
    text_products = ''
    start_text = '✅ В наличии следующие позиции (цена за бутылку):\n\n'
    for i in products:
        i = [str(z) for z in i]
        str_product = ' – '.join(i)
        text_products += f"{str_product} рублей\n\n"

    await call.message.answer(text=start_text + text_products, reply_markup=cancel_assort)

@dp.callback_query_handler(text='sticks')
async def sticks_asort(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM sticks')
    products = cur.fetchall()
    text_products = ''
    start_text = '✅ В наличии следующие позиции (цена за бутылку):\n\n'
    for i in products:
        i = [str(z) for z in i]
        str_product = ' - '.join(i)
        text_products += f"{str_product} рублей\n\n"

    await call.message.answer(text=start_text + text_products, reply_markup=cancel_assort)


@dp.callback_query_handler(text='cancel_assort')
async def cancel_assortment(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Выберите категорию товаров:', reply_markup=choice_assortment)

@dp.callback_query_handler(text='cancel')
async def cancel_menu(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


@dp.message_handler(Text(equals=['📩 Заказать', 'Заказать']))
async def forms_menu(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM ban WHERE chat_id = {message.from_user.id}')
    rows_user = cur.fetchall()
    if len(rows_user) == 0:
        await message.answer('Для оформления заказа нажмите на кнопку "Заполнить форму"\n\n'
                             'После отправки формы с Вами свяжется менеджер и уточнит все детали'
                             ,
                             reply_markup=forms_start)
    else:
        await message.answer('Вы забанены и не можете совершать заказы в нашем боте. Для разбана напишите @mmmtvvv')

@dp.callback_query_handler(text='forms')
async def start_form(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer(text='1. Напишите ФИО', reply_markup=ReplyKeyboardRemove())
    await Forms.first()

@dp.callback_query_handler(text='assort', state=Forms.assort)
async def assort_forms(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    #await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Выберите категорию товаров:', reply_markup=s_choice_assortment)

@dp.callback_query_handler(text='cancel', state=Forms.assort)
async def s_cancel_assortment(call: CallbackQuery, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

@dp.callback_query_handler(text='sigs', state=Forms.assort)
async def s_sigs_asort(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM sigs')
    products = cur.fetchall()
    text_products = ''
    start_text = '✅ В наличии следующие позиции (цена за бутылку):\n\n'
    for i in products:
        i = [str(z) for z in i]
        str_product = ' – '.join(i)
        text_products += f"{str_product} рублей\n\n"

    await call.message.answer(text=start_text + text_products, reply_markup=cancel_assort)

@dp.callback_query_handler(text='snus', state=Forms.assort)
async def s_snus_asort(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM snus')
    products = cur.fetchall()
    text_products = ''
    start_text = '✅ В наличии следующие позиции (цена за бутылку):\n\n'
    for i in products:
        i = [str(z) for z in i]
        str_product = ' – '.join(i)
        text_products += f"{str_product} рублей\n\n"

    await call.message.answer(text=start_text + text_products, reply_markup=cancel_assort)

@dp.callback_query_handler(text='hqd', state=Forms.assort)
async def s_hqd_asort(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM hqd')
    products = cur.fetchall()
    text_products = ''
    start_text = '✅ В наличии следующие позиции (цена за блок):\n\n'
    for i in products:
        i = [str(z) for z in i]
        str_product = ' – '.join(i)
        text_products += f"{str_product} рублей\n\n"

    await call.message.answer(text=start_text + text_products, reply_markup=cancel_assort)

@dp.callback_query_handler(text='sticks', state=Forms.assort)
async def s_sticks_asort(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM sticks')
    products = cur.fetchall()
    text_products = ''
    start_text = '✅ В наличии следующие позиции (цена за бутылку):\n\n'
    for i in products:
        i = [str(z) for z in i]
        str_product = ' – '.join(i)
        text_products += f"{str_product} рублей\n\n"

    await call.message.answer(text=start_text + text_products, reply_markup=cancel_assort)

@dp.callback_query_handler(text='cancel_assort', state=Forms.assort)
async def s_cancel_assortment_menu(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Выберите категорию товаров:', reply_markup=s_choice_assortment)

@dp.message_handler(state=Forms.name)
async def fio(message: types.Message, state: FSMContext):

    name = message.text

    await state.update_data(
        {"name": name}
    )

    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    await message.answer('2. Напишите адрес (город, улицу, номер дома)')

    await Forms.next()

@dp.message_handler(state=Forms.adress)
async def adress(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    adress = message.text

    await state.update_data(
        {"adress": adress}
    )

    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    await message.answer('3. Напишите номер телефона')

    await Forms.next()

@dp.message_handler(state=Forms.number)
async def number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    adress = data.get('adress')
    number = message.text

    await state.update_data(
        {"number": number}
    )

    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    await message.answer(text='4. Напишите название позиций и кол-во бутылок', reply_markup=forms)

    await Forms.next()

@dp.message_handler(state=Forms.assort)
async def assort(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    adress = data.get('adress')
    number = data.get('number')
    assort = message.text

    await state.update_data(
        {"assort": assort}
    )

    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute(f'SELECT chat_id FROM first_sale WHERE chat_id = {message.from_user.id}')
    rows = cur.fetchall()
    if len(rows) == 0:
        fs = 'Нет первой скидки'
    else:
        fs = 'Есть первая скидка'

    user_id = message.from_user.username
    chat_id = message.from_user.id


    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    await message.answer('Заказ сформирован! В ближайшее время с Вами свяжется менеджер\n',
                         reply_markup=start_menu)

    await bot.send_message(chat_id=admin_id,
                           text='Пришёл заказ!\n\n'
                           
                           f'{name}\n'
                           f'{adress}\n'
                           f'{number}\n'
                           f'{assort}\n'
                           f'@{user_id}\n'
                           f'{chat_id}\n'
                           f'{fs}'
                           )

    await message.answer('🍺 Добро пожаловать в PIVO 2 PIVO!\n \n'
                         '✅ У нас Вы найдете учшие сорта пива по доступным ценам\n \n'
                         '📩 Для получения дополнительной информации используйте меню бота', reply_markup=start_menu)

    await state.finish()

