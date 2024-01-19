import logging
from config import admin
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Dispatcher

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.utils import executor

from expider_keys import get_expired_keys_info
from handlers.handlers import get_key_command, my_info, process_callback_payment_method
from handlers.handlers_change_location import change_location_handlers
from handlers.send_all import *
from handlers.admin_command import user_info_command
from text import not_bot_text, instruction
from handlers.handlers_mykeys import *
from aiogram import types
from logger import logger
from user_data import if_new_user
from keyboards.keyboards import capcha

User_Data = UserData()
my_keys
get_key_command
user_info_command
show_rassilka
get_posttext
get_photo
get_photo_id
get_video
get_video_id
get_testpost
sendposts
cancel_post
subscribe
my_info

process_callback_payment_method
change_location_handlers

scheduler = AsyncIOScheduler()


@dp.message_handler(commands=['start'], state="*")
async def process_start_command(message: types.Message):

    telegram_id = message.from_user.id
    username = message.from_user.first_name
    last_name = message.from_user.last_name
    nickname = message.from_user.username
    language = message.from_user.language_code
    premium = message.from_user.is_premium
    referer_user_id = message.get_args()


    logger.info(f"start command {telegram_id}, {username}, {nickname}")
    try:
        new_user = if_new_user(telegram_id, username, referer_user_id, last_name, nickname, language, premium)
        if not new_user:
            with open('images/menu.jpeg', 'rb') as photo:
                await bot.send_photo(chat_id=telegram_id,
                                     photo=photo,
                                     caption=instruction,
                                     parse_mode="HTML",
                                     reply_markup=main_menu_inline())
                return

        if referer_user_id:
            referer_telegram_id = User_Data.get_tg_if_use_user_id(referer_user_id)
            if referer_telegram_id:
                await bot.send_message(referer_telegram_id, "По вашей ссылке приглашен новый пользователь!")

        await message.reply(not_bot_text,
                            parse_mode="HTML",
                            disable_web_page_preview=True,
                            reply_markup=capcha(),
                            )

        logging.info(f"INFO: NEW USER - tg : {telegram_id}, "
                     f"username : {username}, "
                     f"{referer_user_id}")
        await bot.send_message(chat_id=err_send, text=f"INFO: NEW USER - tg : {telegram_id}, "
                                                      f"username : {username},"
                                                      f"{referer_user_id}")
        await bot.send_message(chat_id=admin, text=f"INFO: NEW USER - tg : {telegram_id}, "
                                                      f"username : {username},"
                                                      f"{referer_user_id}")

    except Exception as e:
        await bot.send_message(err_send, f"Ошибка при регистрации нового пользователя ошибка - {e}")
        logging.error(f"ERROR: NEW USER - Ошибка при добавлении нового пользователя "
                      f"tg - {telegram_id}, "
                      f"ошибка - {e}")


@dp.callback_query_handler(lambda c: c.data == "not_bot", state="*")
async def start_to_use_bot(callback_query: types.CallbackQuery):
    telegram_id = callback_query.message.chat.id
    user_id = User_Data.get_user_id(telegram_id)

    # удаляем капчу
    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")
    logger.info(f"Капча пройдена user_id - {user_id}")

    # kb_free_tariff = free_tariff()

    # отправялем пиветственный текст
    with open('images/menu.jpeg', 'rb') as photo:
        await bot.send_photo(chat_id=callback_query.message.chat.id,
                             photo=photo,
                             caption=instruction,
                             parse_mode="HTML",
                             reply_markup=main_menu_inline())

    # предлагаем пользователю тестовый период
    # await bot.send_message(chat_id=telegram_id,
    #                        text=promotion_text,
    #                        reply_markup=kb_free_tariff,
    #                        parse_mode="HTML",
    #                        )
    logger.info(f'Предложен тестовый период user - {user_id}')



def job_function():
    get_expired_keys_info()
async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)
    # Уведомляет про запуск
    await on_startup_notify(dispatcher)


async def on_startup_notify(dp: Dispatcher):
    await dp.bot.send_message(err_send, "Бот Запущен")

if __name__ == '__main__':
    # scheduler.add_job(job_function, IntervalTrigger(seconds=3))
    # scheduler.start()

    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
    logger.info('Бот запущен')
