from config import file_ids, bot
import asyncio

from handlers.handlers import get10days
from keyboards.keyboards import *

from user_data import execute_query
from logger import logger

bills_text = """Мы заметили, что вы хотели про"""

answer = """🎁 <b>ПОДАРОК ДЛЯ ВАС </b>🎁

✅ Подпишитесь на канал и получите 10 дней высокоскоростного VPN БЕСПЛАТНО!
"""
# present = """🎁 <b>ПОДАРОК ДЛЯ ВАС </b>🎁
#
# Пользуйтесь 10 дней стабильным VPN бесплатно! Жмите, чтобы получить ключ 👇
# """

march8 = """
<b>Дорогие женщины!</b>

Сердечно поздравляю вас с чудесным весенним праздником — 8 Марта! 
Этот день наполнен нежностью первых весенних лучей, ароматом пробуждающейся природы и, конечно же, восхищением вашей неисчерпаемой красотой и женственностью.

PS. Напоминаем, что у нас действует скидка - 50%  по промо-коду <code><b>«8MARCH»</b></code>
Осталось 2 дня😉
"""

sql_from_biils = """SELECT users.telegram_id
    FROM users JOIN bills ON users.user_id = bills.user_id
    WHERE bills.notify = 0
    AND bills.bill_date <= NOW() - INTERVAL 1 HOUR"""


async def get_users_not_use_trial():
    # sql = """SELECT telegram_id
    #         FROM users
    #         WHERE message = 0
    #         AND free_tariff = 0
    #         AND date_accession <= NOW() - INTERVAL 1 HOUR"""
    sql = """SELECT telegram_id
                FROM users
                WHERE message2 = 0"""
    #
    # """SELECT user_keys.name FROM
    #                            users JOIN user_keys ON users.user_id = user_keys.user_id
    #                                WHERE users.user_id = %s"""

    result = execute_query(sql)

    logger.info('Пошел поиск')

    list_telegram_id = []

    logger.info(f"нашли {len(list_telegram_id)} пользователей")

    for tg in result:
        list_telegram_id.append(tg[0])

    return list_telegram_id


async def get_keyboard(telegram_id):
    query = """SELECT    uk.key_id FROM     users u LEFT JOIN
         user_keys uk ON u.user_id = uk.user_id WHERE     u.telegram_id = %s"""

    result = execute_query(query, (telegram_id,))

    if not result[0][0]:
        return get_key()
    return prolong()


async def sender_promo_txt():
    # здесь список всех, кому нужно отправить сообщение
    lst_tgs = await get_users_not_use_trial()

    # sql_update_message = 'UPDATE users SET message = 1 WHERE telegram_id = %s'
    sql_update_message = 'UPDATE users SET message2 = 1 WHERE telegram_id = %s'

    count = 0
    count2 = 0
    if lst_tgs:
        for telegram_id in lst_tgs:
            try:

                keyboard = await get_keyboard(telegram_id)

                await bot.send_photo(chat_id=telegram_id,
                                     photo=file_ids['march8'],
                                     caption=march8,
                                     reply_markup=keyboard,
                                     parse_mode="HTML")
                logger.info(f"Сообщение отправлено")

                execute_query(sql_update_message, (telegram_id,))

                count += 1
            except Exception as e:

                logger.error(f"{telegram_id}, сообщение не отправлено ошибка - {e}")

    if count:
        logger.info(f'Промо текс отправлен {count} юзерам , Не доставлено  - {count2}')


async def main():
    while True:
        await sender_promo_txt()
        await asyncio.sleep(777)  # Используйте asyncio.sleep() вместо time.sleep() в асинхронном коде


if __name__ == '__main__':
    asyncio.run(main())
