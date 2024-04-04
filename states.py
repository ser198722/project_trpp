from aiogram.dispatcher.filters.state import StatesGroup, State


class Forms(StatesGroup):
    name = State()
    adress = State()
    number = State()
    assort = State()


class Create(StatesGroup):
    product = State()
    price = State()


class Delete(StatesGroup):
    product = State()


class Update(StatesGroup):
    product = State()
    price = State()


class Mailing(StatesGroup):
    mail_text = State()


class Ban(StatesGroup):
    ban = State()
    re_ban = State()


class Ref_code(StatesGroup):
    input_code = State()


class Ref_check(StatesGroup):
    ref_code = State()
