import logging

from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.utils import executor

from handlers.handlers import get_key_command, my_info, choice_free_tariff
# from handlers.notifikation import anypay_notification, app
from handlers.send_all import *
from handlers.admin_command import user_info_command
from handlers.handlers_referal_program import process_partners_command
from handlers.handlers_balance import balance_command, replenish_balance_comand, get_amount
from logic_keys.expider_keys import get_expired_keys_info
from sender import on_startup_notify
from text import start_text, promotion_text
from handlers.handlers_all_country import select_country

from handlers.handlers_mykeys import *

from get_conn import create_connection

from aiogram import types

from logger import logger
from user_data import if_new_user

mydb = create_connection()

select_country
get_key_command
process_partners_command
replenish_balance_comand
balance_command
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
choice_free_tariff
free_tariff
# anypay_notification
get_amount

scheduler = AsyncIOScheduler()


async def job_function():
    await get_expired_keys_info()


@dp.message_handler(commands=['start'], state="*")
async def process_start_command(message: types.Message):
    logger.info("start command")
    telegram_id = message.from_user.id
    username = message.from_user.first_name
    referer_user_id = message.get_args()
    logger.info(f"start command {telegram_id}, {username}")
    try:
        new_user = await if_new_user(telegram_id, username, referer_user_id)
        kb_subscribe = free_tariff()
        User_Data = UserData()
        if not new_user:
            await message.reply(instruction,
                                parse_mode="HTML",
                                disable_web_page_preview=True,
                                reply_markup=main_menu())
            return

        if referer_user_id:
            referer_telegram_id = User_Data.get_tg_if_use_user_id(referer_user_id)
            if referer_telegram_id:
                await bot.send_message(referer_telegram_id, "По вашей ссылке приглашен новый пользователь!")

        await message.reply(start_text,
                            parse_mode="HTML",
                            disable_web_page_preview=True,
                            reply_markup=main_menu(),
                            )
        await bot.send_message(chat_id=telegram_id,
                               text=promotion_text,
                               reply_markup=kb_subscribe,
                               parse_mode="HTML",
                               )
        logging.info(f"INFO: NEW USER - tg : {telegram_id}, "
                     f"username : {username}, "
                     f"{referer_user_id}")
        await bot.send_message(chat_id=err_send, text=f"INFO: NEW USER - tg : {telegram_id}, "
                                                      f"username : {username},"
                                                      f"{referer_user_id}")
    except Exception as e:
        await bot.send_message(err_send, f"Ошибка при регистрации нового пользователя ошибка - {e}")
        logging.error(f"ERROR: NEW USER - Ошибка при добавлении нового пользователя "
                      f"tg - {telegram_id}, "
                      f"ошибка - {e}")


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)
    # WEBHOOK_URL = "https://telegram.outlinevpn.space/notification"

    WEBHOOK_URL = "https://telegram.outlinevpn.space/notification"  # Замените на ваш URL
    webhook_info = await bot.set_webhook(url=WEBHOOK_URL)
    print(webhook_info)

    # await if_new_user(64793659666, 'MISAQ', None)

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    scheduler.add_job(job_function, IntervalTrigger(days=1))
    scheduler.start()
    # app.run(host='217.28.220.74', port=8080)
    executor.start_polling(dp, on_startup=on_startup, skip_updates=False)
    logger.info('Бот запущен')
