from aiogram.dispatcher.filters.state import State, StatesGroup


class MyForm(StatesGroup):
    # описание операций
    category = State()
    category_history = State()
    category_id = State()
    category_type = State()
    description = State()
    value = State()
    msg_id = State()
