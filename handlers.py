from aiogram.dispatcher.filters import CommandStart, Text
from aiogram.types import (Message, InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery, LabeledPrice, PreCheckoutQuery, ReplyKeyboardRemove)
from aiogram.utils.callback_data import CallbackData

from config import admin_id
from load_all import dp, bot
from keyboard import start_menu

@dp.message_handler(CommandStart())
async def start_message(message: types.Message):

    await message.answer('🍺 Добро пожаловать в PIVO 2 PIVO!\n \n' 
                         '✅ У нас Вы найдете лучшие сорта пива по доступным ценам\n \n'
                         '📩 Для получения дополнительной информации используйте клавиатуру бота', reply_markup=start_menu)
