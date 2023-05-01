from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from api import api
from locale_middleware import i18n as _


async def get_profit_kbs(
        tg_id: str,
        category: str = "profit",
        parent_id: int = None,
        is_final: bool = True,
        locale: str = "ru"
):
    resp_json_list: list = await api.get_types(tg_id, category=category, parent_id=parent_id, is_final=is_final)
    row_width = 2
    keyboard = InlineKeyboardMarkup(row_width=row_width)
    for i in range(len(resp_json_list)):
        start_index = i * row_width
        end_index = min((i + 1) * row_width, len(resp_json_list))
        row_buttons = []
        for j in range(start_index, end_index):
            is_final = "_yes" if resp_json_list[j]['is_final'] is True else "_no"
            row_buttons.append(
                InlineKeyboardButton(
                    resp_json_list[j]['name_' + locale],
                    callback_data=category + "_" +
                                  str(resp_json_list[j]['id']) + is_final

                )
            )
        keyboard.add(*row_buttons)
    keyboard.add(InlineKeyboardButton(_("На главную"), callback_data="main_page"))
    return keyboard


def only_cancel_btn():
    buttons = [
        InlineKeyboardButton(text=_("Отмена"), callback_data="cancel")
    ]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    return keyboard


def submit_keyboard_btn():
    buttons = [
        InlineKeyboardButton(text=_("Да"), callback_data="submit"),
        InlineKeyboardButton(text=_("Отмена"), callback_data="cancel")
    ]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    return keyboard


def languages_keyboard_btn():
    buttons = [
        InlineKeyboardButton(text="🇺🇿", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇺🇸", callback_data="lang:en"),
    ]
    keyboard = InlineKeyboardMarkup(row_width=3).add(*buttons)
    return keyboard


def main_reply_keyboards():
    buttons = [
        InlineKeyboardButton(text=_("Доходы"), callback_data="doxod"),
        InlineKeyboardButton(text=_("Расходы"), callback_data="rasxod"),
        InlineKeyboardButton(text=_("Изменение языка"), callback_data="change_lang"),
        InlineKeyboardButton(text=_("Отчеты"), callback_data="report")
    ]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    return keyboard


def lazy_main_button(locale):
    buttons = [
        InlineKeyboardButton(text=_("Доходы", locale=locale), callback_data="doxod"),
        InlineKeyboardButton(text=_("Расходы", locale=locale), callback_data="rasxod"),
        InlineKeyboardButton(text=_("Изменение языка", locale=locale), callback_data="change_lang"),
        InlineKeyboardButton(text=_("Отчеты", locale=locale), callback_data="report")
    ]
    keyboard = InlineKeyboardMarkup(row_width=2).add(*buttons)
    return keyboard
