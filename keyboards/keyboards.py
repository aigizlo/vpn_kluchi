from aiogram import types
from config import tg_channel_link, article
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import one_month, three_month, one_year

server_id_country = {
    1: '🇩🇪Германия Франкфурт',
    2: '🇺🇸Америка Лос Анджелес'
}


# генерируем имена ключей для выбора одного из них для смены локации
def generate_key_buttons_for_exchange(name_keys):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for name in name_keys:
        keyboard.add(
            InlineKeyboardButton(text=f"«Ключ № {name[0]}»", callback_data=f"selecting_key_for_exchange:{name[0]}"))

    keyboard.add(InlineKeyboardButton(text="⬅️Назад", callback_data="go_back"))

    return keyboard


# генерация кнопок для продления
def generate_key_buttons(name_keys):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for name in name_keys:
        keyboard.add(InlineKeyboardButton(text=f"«Ключ №{name[0]}»", callback_data=f"select_key:{name[0]}"))

    keyboard.add(InlineKeyboardButton(text="⬅️Назад", callback_data="go_back"))

    return keyboard


# генерим имена серверов
def generate_location_button(servers):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for server in servers:
        location = server_id_country.get(server)
        keyboard.add(InlineKeyboardButton(text=location, callback_data=f"select_country_for_exchange:{server}"))
    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="go_back"))

    return keyboard


def capcha():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Я не робот", callback_data="not_bot"),
    )
    return keyboard


def keyboard_if_not_keys():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("✅ Получить ключ", callback_data="get_keys"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="go_back"),
    )
    return keyboard


def keyboard_if_have_keys():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("📍 Сменить локацию", callback_data="exchange_keys"),
        types.InlineKeyboardButton("⌛ Продлить ключи", callback_data="prolong_keys"),
        # types.InlineKeyboardButton("✅ Получить ключ", callback_data="get_keys"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="go_back"),
    )
    return keyboard


def plus_balance():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Пополнить баланс")
    )
    return keyboard


# клавиатура где пользователю предлагаем подписаться на канал
def subscribe():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("✅ Подписаться на канал", url=tg_channel_link),
        types.InlineKeyboardButton("🔁 Проверить подписку", callback_data="subscribe_check"),

    )
    return keyboard


# Cпособы оплаты
def kb_pay(amount, fk_link=None):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        # types.InlineKeyboardButton(f"FREE KASSA - {amount} рублей", url=fk_link),
        # types.InlineKeyboardButton(f"ANY PAY - {amount} рублей", url=any_pay_link),
        types.InlineKeyboardButton(f"💳 Оплата онлайн - {amount} рублей", url=fk_link),
        types.InlineKeyboardButton("💰Оплата с партнерского счета", callback_data=f"balance_ref:{amount}"),
        types.InlineKeyboardButton("Отмена", callback_data="go_back")
    )
    return keyboard


def kb_pay2(amount, fk_link=None):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        # types.InlineKeyboardButton(f"FREE KASSA - {amount} рублей", url=fk_link),
        # types.InlineKeyboardButton(f"ANY PAY - {amount} рублей", url=any_pay_link),
        types.InlineKeyboardButton(f"💳 Оплата онлайн - {amount} рублей", url=fk_link),
        # types.InlineKeyboardButton("💰Оплата с партнерского счета", callback_data=f"balance_ref:{amount}"),
        types.InlineKeyboardButton("Отмена", callback_data="go_back")
    )
    return keyboard


def online_pay(fk_link):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        # types.InlineKeyboardButton("💳ANY PAY", url=any_pay_link),
        types.InlineKeyboardButton("💳Оплата онлайн", url=fk_link),
    )
    return keyboard


# Получить ключ
def choice_period():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(f"10 дней в подарок 🎁", callback_data=f'get_present'),
        types.InlineKeyboardButton(f"1 месяц – {one_month} ₽.", callback_data=f'payment_method:{one_month}'),
        types.InlineKeyboardButton(f"3 месяца – {three_month} ₽ (1 мес в 🎁)",
                                   callback_data=f"payment_method:{three_month}"),
        types.InlineKeyboardButton(f"1 год – {one_year} ₽ (4 мес. в 🎁)", callback_data=f"payment_method:{one_year}"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="go_back")
    )
    return keyboard


# Получить ключ без бесплатного
def choice_period_not_free():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(f"1 месяц – {one_month} ₽.", callback_data=f'payment_method:{one_month}'),
        types.InlineKeyboardButton(f"3 месяца – {three_month} ₽ (1 мес в 🎁)",
                                   callback_data=f"payment_method:{three_month}"),
        types.InlineKeyboardButton(f"1 год – {one_year} ₽ (4 мес. в 🎁)", callback_data=f"payment_method:{one_year}"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="go_back")
    )
    return keyboard


# для выбора месяца, на который будет продлеваться ключ
def choice_renewal_period():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(f"1 месяц – {one_month} ₽.", callback_data=f'renewal:{one_month}'),
        types.InlineKeyboardButton(f"3 месяца – {three_month} ₽ (1 мес в 🎁)",
                                   callback_data=f"renewal:{three_month}"),
        types.InlineKeyboardButton(f"1 год – {one_year} ₽ (4 мес. в 🎁)", callback_data=f"renewal:{one_year}"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="go_back")
    )
    return keyboard


# Cпособы оплаты
# def get_pay_method_keyboard():
#     keyboard = types.InlineKeyboardMarkup(row_width=1)
#     keyboard.add(
#         types.InlineKeyboardButton("💰any pay", callback_data=f"any_pay"),
#         types.InlineKeyboardButton("💳fro pay", callback_data="fro_pay"),
#         types.InlineKeyboardButton("💰Оплата с партнерского счета", callback_data="balance_ref"),
#         types.InlineKeyboardButton("❌Отмена", callback_data="go_back")
#     )
#     return keyboard

def main_menu_inline():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("📹 Видео-инструкция", callback_data=f"video_inst"),
        types.InlineKeyboardButton("🔐 Получить ключ", callback_data=f"get_keys"),
        types.InlineKeyboardButton('🔑 Мои ключи', callback_data=f"my_keys"),
        types.InlineKeyboardButton('💸 Зарабатывай с нами', callback_data=f"partners"),
        types.InlineKeyboardButton('💡 Почему мы?', callback_data='why_we'))

    return keyboard


def in_main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("📹 Видео-инструкция", callback_data=f"video_inst"),
        types.InlineKeyboardButton("⬅️ Главное меню", callback_data=f"main_menu"),
    )
    return keyboard


def back():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🔙Назад", callback_data="go_back")
    )
    return keyboard


# def back_and_prolong_inline_button():
#     keyboard = types.InlineKeyboardMarkup(row_width=2)
#     prolong_button = types.InlineKeyboardButton('⌛️Продлить действие', callback_data='prolong_keys')
#     buy_button = types.InlineKeyboardButton('🔐Получить новый ключ', callback_data='get_keys')
#     button_back = types.InlineKeyboardButton('🔙Назад', callback_data='go_back')
#     keyboard.add(prolong_button, buy_button, button_back)
#
#     return keyboard


def back_and_withdraw_inline():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    withdraw_button = types.InlineKeyboardButton('🤑 Вывод средств', callback_data='withdraw_bonus')
    button_back = types.InlineKeyboardButton('⬅️ Главное меню', callback_data='go_back')
    keyboard.add(withdraw_button, button_back)

    return keyboard


def cancel():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_back = types.InlineKeyboardButton('⬅️ Назад', callback_data='go_back')
    keyboard.add(button_back)

    return keyboard


def in_main_menu():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_back = types.InlineKeyboardButton('⬅️ Главное меню', callback_data='go_back')
    keyboard.add(button_back)

    return keyboard


def presenr10():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_back = types.InlineKeyboardButton('✅ Получить ключ', callback_data='get10days')
    keyboard.add(button_back)

    return keyboard


def get_key():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("✅Получить ключ со скидкой", callback_data="get_keys"),
    )
    return keyboard


def prolong():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("⌛Продлить ключ со скидкой", callback_data="prolong_keys"),

    )
    return keyboard


