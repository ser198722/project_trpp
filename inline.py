from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

cancel = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Назад', callback_data="cancel")
    ]
]

)

choice_assortment = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Страна', callback_data="sigs"), InlineKeyboardButton(text='Объем', callback_data="snus")
        ],
        [
            InlineKeyboardButton(text='Крепость', callback_data="hqd"), InlineKeyboardButton(text='Вкус', callback_data="sticks")
        ],
        [InlineKeyboardButton(text='Назад', callback_data="cancel")]
    ], resize_keyboard=True
)

forms_start = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Заполнить форму', callback_data='forms')],
        [InlineKeyboardButton(text='Назад', callback_data='cancel')]
    ], resize_keyboard=True
)

forms = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Ассортимент', callback_data='assort')]
    ], resize_keyboard=True
)

cancel_assort = InlineKeyboardMarkup(
    inline_keyboard=[

        [InlineKeyboardButton(text='Назад', callback_data="cancel_assort")]

    ], resize_keyboard=True
)

s_choice_assortment = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Страна', callback_data="sigs"), InlineKeyboardButton(text='Объем', callback_data="snus")
        ],
        [
            InlineKeyboardButton(text='Крепость', callback_data="hqd"), InlineKeyboardButton(text='Вкус', callback_data="sticks")
        ]

    ], resize_keyboard=True
)

stats_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='cancel_admin')]
    ], resize_keyboard=True
)

admin_panel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='✅ Добавить товар', callback_data='add'),
            InlineKeyboardButton(text='❌ Удалить товар', callback_data='delete'),
        ],
        [
            InlineKeyboardButton(text='🔧 Редактировать цену', callback_data='update')
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='cancel_admin')
        ]
    ], resize_keyboard=True
)

update_callback = CallbackData('buy', 'category_update', 'base_name')
panel_update_assortment = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Страна', callback_data="buy:sigs_update:sigs"), InlineKeyboardButton(text='Объем', callback_data="buy:snus_update:snus")
        ],
        [
            InlineKeyboardButton(text='Крепость', callback_data="buy:hqd_update:hqd"), InlineKeyboardButton(text='Вкус', callback_data="buy:sticks_update:sticks")
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='cancel_admin')
        ]
    ], resize_keyboard=True
)

add_callback = CallbackData('buy', 'category_add', 'base_name')
panel_choice_assortment = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Страна', callback_data="buy:sigs_add:sigs"), InlineKeyboardButton(text='Объем', callback_data="buy:snus_add:snus")
        ],
        [
            InlineKeyboardButton(text='Крепость', callback_data="buy:hqd_add:hqd"), InlineKeyboardButton(text='Вкус', callback_data="buy:sticks_add:sticks")
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='cancel_admin')
        ]

    ], resize_keyboard=True
)

delete_callback = CallbackData('buy', 'category_delete', 'base_name')
panel_delete_assortment = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Страна', callback_data="buy:sigs_delete:sigs"), InlineKeyboardButton(text='Объем', callback_data="buy:snus_delete:snus")
        ],
        [
            InlineKeyboardButton(text='Крепость', callback_data="buy:hqd_delete:hqd"), InlineKeyboardButton(text='Вкус', callback_data="buy:sticks_delete:sticks")
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='cancel_admin')
        ]

    ], resize_keyboard=True
)


ban_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Забанить', callback_data='ban'),
            InlineKeyboardButton(text='Разбанить', callback_data='re_ban')
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='cancel_admin')
        ]
    ], resize_keyboard=True
)


ref_choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Моя скидка', callback_data='ref_info'),
            InlineKeyboardButton(text='Ввести код', callback_data='ref_code')
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='cancel')
        ]
    ], resize_keyboard=True
)

