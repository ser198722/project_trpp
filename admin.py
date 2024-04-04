from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Text, Command
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove)
from aiogram.utils.callback_data import CallbackData

from config import admin_id
from load_all import dp, bot

import sqlite3
from config import admin_id
from states import Create, Delete, Update, Mailing, Ban, Ref_check
from inline import stats_cancel, admin_panel, panel_choice_assortment, add_callback, panel_delete_assortment,\
    delete_callback, panel_update_assortment, update_callback, ban_choice

@dp.message_handler(Command('admin'), chat_id=admin_id)
async def admin_start(message: types.Message):
    db = sqlite3.connect('users.db')
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS ban (chat_id BIGINT)")
    db.commit()

    await message.answer('👨‍💻 Доступные комманды для администратора:\n\n'
                         '/product - добавление и удаление товаров\n'
                         '/stats - кол-во активных пользователей\n'
                         '/mailing - запуск рассылки\n'
                         '/referals - работа с реферальной системой\n'
                         '/ban - бан и разбан пользователей')


@dp.message_handler(Command('ban'), chat_id=admin_id)
async def start_ban(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer(text='Выберите действие', reply_markup=ban_choice)

@dp.callback_query_handler(text='ban')
async def ban(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Введите id пользователя для бана')
    await Ban.ban.set()

@dp.message_handler(state=Ban.ban)
async def add_ban(message: types.Message, state: FSMContext):
    chat = message.text
    db = sqlite3.connect('users.db')
    cur = db.cursor()


    cur.execute(f'SELECT * FROM ban WHERE chat_id = {chat}')
    rows_user = cur.fetchall()
    if len(rows_user) == 0:
        cur.execute(f'INSERT INTO ban VALUES(?)', (chat,))
        db.commit()
    await message.answer('Пользователь забанен!')

    await state.finish()


@dp.callback_query_handler(text='re_ban')
async def ban(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Введите id пользователя для разбана')
    await Ban.re_ban.set()

@dp.message_handler(state=Ban.re_ban)
async def add_ban(message: types.Message, state: FSMContext):
    chat = message.text

    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute(f'DELETE FROM ban WHERE chat_id = {chat}')
    db.commit()

    await message.answer('Пользователь разбанен!')

    await state.finish()


@dp.message_handler(Command('referals'), chat_id=admin_id)
async def start_referals(message: types.Message):
    await message.answer('Введите chat_id пользователя, чтобы проверить '
                         'наличие первой скидки, реферальной скидки и '
                         'кол-ва рефералов', reply_markup=stats_cancel)
    await Ref_check.first()


@dp.message_handler(state=Ref_check.ref_code)
async def ref_check(message: types.Message, state: FSMContext):
    code = message.text
    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute(f'SELECT chat_id FROM first_sale WHERE chat_id = {code}')
    fs_c = cur.fetchone()
    if fs_c == None:
        fs = 'Нет первой скидки'
    else:
        fs = 'Есть первая скидка'

    cur.execute(f'SELECT code FROM users WHERE chat_id = {code}')
    cd = cur.fetchone()

    cur.execute(f'SELECT count_ref FROM users WHERE code = {cd[0]}')
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

    await message.answer(f'{fs}\n'
                         f'Количество рефералов – {count}\n'
                         f'Cкидка - {sale} %'
                         )

    await state.finish()

@dp.message_handler(Command('mailing'), chat_id=admin_id)
async def start_mailing(message: types.Message):
    await message.answer('Введите текст рассылки')
    await Mailing.first()

@dp.message_handler(state=Mailing.mail_text)
async def send_text(message: types.Message, state: FSMContext):
    mail_text = message.text
    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute('SELECT chat_id FROM users')
    id_users = cur.fetchall()
    for i in id_users:
        i = [str(z) for z in i]
        str_users = ''.join(i)
        await bot.send_message(chat_id=int(str_users), text=mail_text)

    await bot.send_message(chat_id=admin_id, text='Рассылка запущена!')

    await state.finish()


@dp.message_handler(Command('stats'), chat_id=admin_id)
async def stats(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)

    db = sqlite3.connect('users.db')
    cur = db.cursor()

    cur.execute(f'SELECT * FROM users')
    rows = cur.fetchall()

    await message.answer(text=f'В базе {len(rows)} человек', reply_markup=stats_cancel)


@dp.message_handler(Command('product'), chat_id=admin_id)
async def start_panel(message: types.Message):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await message.answer(text='Воспользуйтесь кнопками для редактирования ассортимента', reply_markup=admin_panel)


@dp.callback_query_handler(text='cancel_admin')
async def cancel_admin(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)


@dp.callback_query_handler(text='update')
async def add_product(call: CallbackQuery):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Выберите категорию редактирования товара', reply_markup=panel_update_assortment)


@dp.callback_query_handler(update_callback.filter(category_update='sigs_update'),state=None)
async def start_update_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара')
    await Update.first()

@dp.callback_query_handler(update_callback.filter(category_update='snus_update'),state=None)
async def start_update_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара')
    await Update.first()

@dp.callback_query_handler(update_callback.filter(category_update='hqd_update'),state=None)
async def start_update_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара')
    await Update.first()

@dp.callback_query_handler(update_callback.filter(category_update='sticks_update'),state=None)
async def start_update_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара')
    await Update.first()


@dp.message_handler(state=Update.product)
async def product_update(message: types.Message, state: FSMContext):
    product = message.text
    await state.update_data(
        {"product": product}
    )
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    await message.answer('Введите новую цену')
    await Update.next()

@dp.message_handler(state=Update.price)
async def price_update(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price = message.text
    base = data.get('base')
    product = data.get('product')
    await state.update_data(
        {"price": price}
    )
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f"UPDATE {base} SET price = {price} where product = '{product}'")
    db.commit()

    await message.answer('Цена изменена!')

    await state.finish()


@dp.callback_query_handler(text='add')
async def add_product(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Выберите категорию добавления товара', reply_markup=panel_choice_assortment)


@dp.callback_query_handler(add_callback.filter(category_add="sigs_add"), state=None)
async def start_add_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара')
    await Create.first()

@dp.callback_query_handler(add_callback.filter(category_add="snus_add"), state=None)
async def start_add_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара')
    await Create.first()

@dp.callback_query_handler(add_callback.filter(category_add="hqd_add"), state=None)
async def start_add_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара')
    await Create.first()

@dp.callback_query_handler(add_callback.filter(category_add="sticks_add"), state=None)
async def start_add_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара')
    await Create.first()


@dp.message_handler(state=Create.product)
async def product_create(message: types.Message, state: FSMContext):
    product = message.text
    await state.update_data(
        {"product": product}
    )
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    await message.answer('Введите цену')
    await Create.next()

@dp.message_handler(state=Create.price)
async def price_create(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price = message.text
    base = data.get('base')
    product = data.get('product')
    await state.update_data(
        {"price": price}
    )
    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    db = sqlite3.connect(f'product.db')
    cur = db.cursor()

    cur.execute(f"CREATE TABLE IF NOT EXISTS {base} (product TEXT, price BIGINT)")
    db.commit()

    cur.execute(f"INSERT INTO {base} VALUES(?,?)", (product, price))
    db.commit()

    await message.answer('Товар добавлен!')

    await state.finish()


@dp.callback_query_handler(text='delete')
async def delete_product(call: CallbackQuery):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    await call.message.answer('Выберите категорию удаления товара', reply_markup=panel_delete_assortment)


@dp.callback_query_handler(delete_callback.filter(category_delete="sigs_delete"), state=None)
async def start_delete_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара для удаления')
    await Delete.first()

@dp.callback_query_handler(delete_callback.filter(category_delete="snus_delete"), state=None)
async def start_delete_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара для удаления')
    await Delete.first()

@dp.callback_query_handler(delete_callback.filter(category_delete="hqd_delete"), state=None)
async def start_delete_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара для удаления')
    await Delete.first()

@dp.callback_query_handler(delete_callback.filter(category_delete="sticks_delete"), state=None)
async def start_delete_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer(cache_time=60)
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    base = callback_data.get('base_name')
    await state.update_data(
        {'base': base}
    )
    state = dp.current_state(chat=call.message.chat.id, user=call.message.from_user.id)

    await call.message.answer(text='Введите название товара для удаления')
    await Delete.first()


@dp.message_handler(state=Delete.product)
async def product_del(message: types.Message, state: FSMContext):
    data = await state.get_data()
    base = data.get('base')
    product = message.text

    state = dp.current_state(chat=message.chat.id, user=message.from_user.id)

    db = sqlite3.connect('product.db')
    cur = db.cursor()

    cur.execute(f"DELETE FROM {base} WHERE product = '{product}'")
    db.commit()

    await message.answer('Товар удален!')

    await state.finish()
