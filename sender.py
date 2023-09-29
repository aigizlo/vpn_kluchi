import asyncio
from aiogram import Dispatcher
from config import bot, err_send


async def send_message(chat_id, text, keyboard=None):
    if keyboard:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")


async def send_message_no_parse_mode(chat_id, text, keyboard=None):
    if keyboard:
        await bot.send_message(chat_id=chat_id, text=text, keyboard=keyboard)
    else:
        await bot.send_message(chat_id=chat_id, text=text)


# Пример использования функции
async def send(chat_id, message_text):
    await send_message(chat_id, message_text)


async def on_startup_notify(dp: Dispatcher):

    await dp.bot.send_message(err_send, "Бот Запущен")
