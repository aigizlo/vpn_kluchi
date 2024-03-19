from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("menu", "Главное меню"),
            types.BotCommand("my_info", "Вывести информацию о себе"),
            types.BotCommand("help", "Техническая поддержка"),
            types.BotCommand("instruction", "Инструкция"),
        ]
    )


adminpanelmenu = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text='С фото 🏞'),
            KeyboardButton(text='С клавиатурой')
        ],
        [
            KeyboardButton(text="Пропустить ➡️")
        ]
    ]
)

adminpanelcontinue = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text='продолжить ➡️')
        ]
    ]
)

lang_buttons = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text='ru'),
            KeyboardButton(text='en')
        ]
    ]
)


startposting = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Подтвердить',callback_data='startposting'),
            InlineKeyboardButton(text='Отменить',callback_data='cancelposting')
        ]
    ]
)