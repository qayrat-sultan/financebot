import logging
import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import FSMContext

from api import api
from config import BOT_TOKEN, redis
from fsm_states import MyForm
from keyboards import get_profit_kbs, only_cancel_btn, submit_keyboard_btn, languages_keyboard_btn, \
    main_reply_keyboards, lazy_main_button
from locale_middleware import i18n, STANDING_USER, FIRST_TIME_USER
from setup import on_startup, on_shutdown

# Configure logging

logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher

bot = Bot(token=BOT_TOKEN)
storage = RedisStorage2()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(i18n)

random_smiles = ["😉", "🫣", "😬", "🤬", "🙅", "😱", "🙈", "🤒", "🎯"]

# Alias for gettext method
_ = i18n.gettext


async def message_editing(message, state, number_error=False, submit=False):
    await message.delete()
    data = await state.get_data()
    category = data.get("category")
    category_history = data.get("category_history")
    msg_id = data.get("msg_id")
    chat_id = data.get("chat_id")
    description = data.get('description')  # dynamic
    value = data.get("value")  # dynamic
    number_error_smile = data.get("number_error_smile")
    result_text = _("Вы выбрали *{category}*: \n{category_history}\n").format(
        category=category, category_history=category_history)

    current_state = await state.get_state()
    if not description and current_state == "MyForm:description":
        result_text += _("Введите описание: ")
    else:
        result_text += _("Ваше описание: *{description}* \n").format(description=description)
    if not value and current_state == "MyForm:value" and number_error is False:
        result_text += _("Введите значение: ")
    elif number_error:
        while True:
            random_smile = random.choice(random_smiles)
            if random_smile != number_error_smile:
                break
        result_text += random_smile + _("Введите только числовое значение: ")
        await state.update_data(number_error_smile=random_smile)
    else:
        result_text += _("Ваше значение: *{value}* \n").format(value=str(value))
    await bot.edit_message_text(
        text=result_text,
        message_id=msg_id,
        chat_id=chat_id,
        parse_mode="MarkdownV2",
        reply_markup=submit_keyboard_btn() if submit else only_cancel_btn()
    )


@dp.message_handler(commands=['start', 'help'], state="*")
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    user_lang = await redis.get(message.from_user.id)
    is_standing_user = True if user_lang[2:] == FIRST_TIME_USER else False
    if is_standing_user:
        await message.reply(_("Здравствуйте, выберите язык"), reply_markup=languages_keyboard_btn())
    else:
        await message.answer(_("Выберите раздел, пожалуйста"),
                             reply_markup=main_reply_keyboards())


@dp.message_handler(state=MyForm.description)
async def process_description2(message: types.Message, state: FSMContext):
    """
    Description
    """
    await state.update_data(description=message.text)
    await MyForm.value.set()
    await message_editing(message, state)


# Check age. Age gotta be digit
@dp.message_handler(lambda message: not message.text.isdigit(), state=MyForm.value)
async def process_value_invalid(message: types.Message, state: FSMContext):
    """
    If age is invalid
    """
    return await message_editing(message, state, number_error=True)


@dp.message_handler(lambda message: message.text.isdigit(), state=MyForm.value)
async def process_value(message: types.Message, state: FSMContext):
    # Update state and data
    await state.update_data(value=int(message.text))
    await message_editing(message, state, submit=True)


""" Callback Handlers """


@dp.callback_query_handler(text="submit", state=MyForm.value)
async def submit_value(callback_query: types.CallbackQuery, state: FSMContext):
    # обработка отправки значения
    # TODO: Здесь нужно отправить в БД данные
    data = await state.get_data()
    category = data.get("category_type")
    category_id = data.get("category_id")
    chat_id = data.get("chat_id")
    description = data.get('description')  # dynamic
    value = data.get("value")  # dynamic
    json_data = {
        "type": category_id,
        "value": value,
        "tg_id": chat_id,
        "tg_name": callback_query.from_user.full_name,
        "name": description
    }
    result = await api.post_request(category=category, data=json_data)
    await callback_query.answer(_("Значение отправляется в базу"))
    await state.finish()
    await callback_query.message.edit_reply_markup(reply_markup=None)
    if result:
        await callback_query.message.answer(_("Данные сохранены в базе ✅"))


@dp.callback_query_handler(lambda call: call.data in ("doxod", "rasxod"), state="*")
async def profit_or_outlay_handler(callback: types.CallbackQuery):
    await callback.answer()
    lang = await redis.get(callback.from_user.id)
    locale = lang.split(":")[0]
    category = "profit" if callback.data == "doxod" else "outlay"
    keyboard = await get_profit_kbs(callback.from_user.id, category=category,
                                    locale=locale)
    await callback.message.edit_text(_("Пожалуйста, выберите категорию"), reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data == "change_lang", state="*")
async def change_lang_handler(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(_("Выберите язык"), reply_markup=languages_keyboard_btn())


@dp.callback_query_handler(lambda call: call.data == "main_page", state="*")
async def back_to_main_page(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(_("Выберите раздел"), reply_markup=main_reply_keyboards())


@dp.callback_query_handler(lambda call: call.data == "report", state="*")
async def back_to_main_page(callback: types.CallbackQuery):
    await callback.answer(_("Подождите"))
    await api.get_report(callback.from_user.id)


@dp.callback_query_handler(lambda call: call.data.startswith('lang'), state="*")
async def language_set(callback: types.CallbackQuery):
    lang = callback.data.split(":")[1]
    lang_text = "Русский"
    if lang == "uz":
        lang_text = "O'zbek"
    elif lang == "en":
        lang_text = "English"
    await callback.answer(_("Выбран {language} язык", locale=lang).format(language=lang_text))
    await redis.set(callback.from_user.id, lang + STANDING_USER)
    await callback.message.edit_text(_("Изменён язык. Выберите раздел", locale=lang),
                                     reply_markup=lazy_main_button(locale=lang))


@dp.callback_query_handler(text="cancel", state="*")
async def submit_value_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer(_("Отменено"))
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await callback.message.delete()
    await state.finish()
    await callback.message.answer(_("Хорошо! Попробуем еще раз."), reply_markup=main_reply_keyboards())


@dp.message_handler(state="*")
async def echo(message: types.Message):
    await message.answer(_("Для пользования ботом напишите /start"))


@dp.callback_query_handler(state="*")
async def echo_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    lang = await redis.get(callback.from_user.id)
    locale = lang.split(":")[0]
    category, pk, is_final = callback.data.split("_")
    if is_final == "no":
        keyboard = await get_profit_kbs(callback.from_user.id, parent_id=pk, is_final=False)
        return await callback.message.edit_reply_markup(reply_markup=keyboard)
    resp = await api.get_history(pk, callback.from_user.id, category=category)
    category_history = resp["category_history"]["history_" + locale]
    if category_history:
        history_list = list(filter(lambda x: x.strip() != "", category_history.split(" > ")))
        category_history = " ".join(["*" + s + "*" for s in history_list])
    category_history += " *" + resp['name_' + locale] + "*"

    category_type = _("Расход") if category == "outlay" else _("Доход")
    await state.set_state(MyForm.category)
    await state.update_data(category=category_type)
    await state.update_data(category_id=pk)
    await state.update_data(category_type=category)
    await state.update_data(category_history=category_history)
    await state.update_data(msg_id=callback.message.message_id)
    await state.update_data(chat_id=callback.message.chat.id)
    await MyForm.description.set()
    text = _("Вы выбрали *{category_type}*: \n{category_history}\nВведите описание:").format(
        category_type=category_type, category_history=category_history
    )
    await callback.message.edit_text(text,
                                     parse_mode="MarkdownV2", reply_markup=only_cancel_btn())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
