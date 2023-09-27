from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import one_month, two_month, three_month, six_month


# # Cпособы оплаты
def generate_prolong_button(key_name):
    keyboard = InlineKeyboardMarkup(row_width=1)

    key_name = [(key_name,)]

    keyboard.add(InlineKeyboardButton(text=f"👉 Продлить ключ «{key_name[0][0]}» 👈",
                                      callback_data=f"select_key:{key_name[0][0]}"))

    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="go_back"))

    return keyboard


# генерация кнопок для продления
def generate_key_buttons(name_keys):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for name in name_keys:
        keyboard.add(InlineKeyboardButton(text=f"«{name[0]}»", callback_data=f"select_key:{name[0]}"))

    keyboard.add(InlineKeyboardButton(text="Отмена", callback_data="go_back"))

    return keyboard


# кнопка для создания промокода
def subscribe():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Подписаться на канал", url="https://t.me/off_radar"),
        types.InlineKeyboardButton("Я уже подписан", callback_data="subscribe_ago"),
        types.InlineKeyboardButton("Нет, спасибо", callback_data="subscribe_no_thanks"),

    )
    return keyboard


# Cпособы оплаты
def get_pay_method_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("💰Cписать с баланса Личного кабинета", callback_data=f"balance_pay_sever"),
        types.InlineKeyboardButton("💳Оплата онлайн", callback_data="online_pay"),
        types.InlineKeyboardButton("Отмена", callback_data="go_back")
    )
    return keyboard


def kb_pay(amount, pay_link):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(f"Перейти к оплате {amount} рублей", url=pay_link)
    )
    return keyboard


def free_tariff():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🎁Попробовать бесплатно", callback_data=f"free_tariff"),
        types.InlineKeyboardButton("Нет, спасибо", callback_data=f"subscribe_no_thanks"),
    )
    return keyboard


def choice_location_free_tariff():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton('🇱🇺Нидерланды – Амстердам', callback_data=f"free_select_country:{1}"),
        types.InlineKeyboardButton('🇩🇪Германия – Франкфурт', callback_data=f"free_select_country:{2}"),
        types.InlineKeyboardButton('🇷🇺Россия – Санкт-Петербург', callback_data=f"free_select_country:{4}"),
        types.InlineKeyboardButton('🇰🇿Казахстан – Астана', callback_data=f"free_select_country:{3}"),
        types.InlineKeyboardButton('🇹🇷Турция – Стамбул', callback_data=f"free_select_country:{5}"),
        types.InlineKeyboardButton("Отмена", callback_data=f"go_back"))
    return keyboard


# для выбора месяца, на который будет продлеваться ключ
def choice_renewal_period():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(f"1 месяц – {one_month} рублей", callback_data=f'renewal:{1}'),
        types.InlineKeyboardButton(f"2 месяца – {two_month} рублей Скидка 10%", callback_data=f"renewal:{2}"),
        types.InlineKeyboardButton(f"3 месяца – {three_month} рублей Скидка 15%", callback_data=f"renewal:{3}"),
        types.InlineKeyboardButton(f"6 месяцев – {six_month} рублей Скидка 30%", callback_data=f"renewal:{6}"),
        types.InlineKeyboardButton("Отмена", callback_data="go_back")
    )
    return keyboard


# кнопка для создания промокода
def promocode():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("Создать промокод", callback_data=f'promo_code'),
        types.InlineKeyboardButton("Отмена", callback_data="go_back")
    )
    return keyboard


# Создание словаря с информацией о тарифных опциях
tariff_options = {
    "amsterdam": [
        ("🇱🇺Амстердам 1 месяц", one_month),
        ("🇱🇺Амстердам 2 месяца", two_month),
        ("🇱🇺Амстердам 3 месяца", three_month),
        ("🇱🇺Амстердам 6 месяцев", six_month)
    ],
    "germany": [
        ("🇩🇪Франкфурт 1 месяц", one_month),
        ("🇩🇪Франкфурт 2 месяца", two_month),
        ("🇩🇪Франкфурт 3 месяца", three_month),
        ("🇩🇪Франкфурт 6 месяцев", six_month)
    ],
    "russia": [
        ("🇷🇺Санкт-Петербург 1 месяц", one_month),
        ("🇷🇺Санкт-Петербург 2 месяца", two_month),
        ("🇷🇺Санкт-Петербург 3 месяца", three_month),
        ("🇷🇺Санкт-Петербург 6 месяцев", six_month)
    ],
    "turkey": [
        ("🇹🇷Стамбул 1 месяц", one_month),
        ("🇹🇷Стамбул 2 месяца", two_month),
        ("🇹🇷Стамбул 3 месяца", three_month),
        ("🇹🇷Стамбул 6 месяцев", six_month)
    ],
    "kz": [
        ("🇰🇿Астана 1 месяц", one_month),
        ("🇰🇿Астана 2 месяца", two_month),
        ("🇰🇿Астана 3 месяца", three_month),
        ("🇰🇿Астана 6 месяцев", six_month)
    ]
}  # Генерация клавиатуры на основе информации из словаря


# генерируем клавиатуру с тарифами
def generate_tariff_keyboard(location):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    buttons = []

    for option in tariff_options[location]:
        button_text, price = option
        button = types.KeyboardButton(f"{button_text} — {price} рублей")
        buttons.append(button)

    buttons.append(types.KeyboardButton('🔙Назад'))
    keyboard.add(*buttons)

    return keyboard


# кнопка Баланс
def balance_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button_balance = types.KeyboardButton('Пополнить баланс')
    button = types.KeyboardButton('🔙Назад'
                                  '')
    keyboard.add(button_balance, button)

    return keyboard


# кнопка Назад
def main_menu():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('🔐Получить ключ')
    button2 = types.KeyboardButton('🔑Мои ключи')
    button3 = types.KeyboardButton('💰Баланс')
    button4 = types.KeyboardButton('💵Партнерская программа')
    # button5 = types.KeyboardButton('Инструкция')
    keyboard.add(button1, button2, button3, button4)

    return keyboard


# Получить ключ
def kb_servers():
    keyboard = types.ReplyKeyboardMarkup(row_width=2)

    button_back = types.KeyboardButton('🔙Назад')

    button_Amsterdam = types.KeyboardButton('🇱🇺Нидерланды – Амстердам')
    button_Germany = types.KeyboardButton('🇩🇪Германия – Франкфурт')
    button_Russia = types.KeyboardButton('🇷🇺Россия – Санкт-Петербург')
    button_KZ = types.KeyboardButton('🇰🇿Казахстан – Астана')
    button_Turkey = types.KeyboardButton('🇹🇷Турция – Стамбул')

    keyboard.add(button_Germany, button_Amsterdam, button_Russia, button_KZ, button_Turkey, button_back)

    return keyboard


def back_button():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    button = types.KeyboardButton('🔙Назад')
    keyboard.add(button)

    return keyboard


def back_and_buy_button():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    buy_button = types.KeyboardButton('🔐Получить ключ')
    button_back = types.KeyboardButton('🔙Назад')
    keyboard.add(buy_button, button_back)

    return keyboard


def back_and_prolong_button():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)

    button_back = types.KeyboardButton('🔙Назад')

    prolong_button = types.KeyboardButton('⌛️Продлить ключи')

    buy_button = types.KeyboardButton('🔐Получить ключ')

    keyboard.add(prolong_button, buy_button, button_back)

    return keyboard


def back_and_withdraw():
    keyboard = types.ReplyKeyboardMarkup(row_width=1)

    button_back = types.KeyboardButton('🔙Назад')

    withdraw = types.KeyboardButton('Вывод средств')

    keyboard.add(withdraw, button_back)

    return keyboard
