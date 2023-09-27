import logging

from config import bot, err_send
from db_conn.get_conn import create_connection
import datetime
from logs.logger import logger

# SQL-запросы
sql_query_check_name = """SELECT user_keys.name FROM 
                            users JOIN user_keys ON users.user_id = user_keys.user_id 
                                WHERE users.user_id = %s"""

sql_select_user_id = "SELECT user_id FROM users WHERE user_id = %s"

sql_select_unused_key = "SELECT * FROM outline_keys WHERE used = 0 AND server_id = %s"

sql_update_key_used = "UPDATE outline_keys SET used = 1 WHERE outline_key_id = %s AND used = 0"

sql_insert_user_key = """INSERT INTO user_keys (user_id, key_id, name, start_date, stop_date)
                           VALUES (%s, %s, %s, %s, %s)"""


async def add_keys(server_id, user_id, key_name, days):
    mydb = create_connection()
    # сроки работы ключа
    start_date = datetime.datetime.now()
    stop_date = start_date + datetime.timedelta(days=days)

    try:
        with mydb.cursor(buffered=True) as mycursor:

            try:
                # обращаемся к бд, чтобы взять неиспользуемый ключ
                mycursor.execute(sql_select_unused_key, (server_id,))
                result_id = mycursor.fetchone()

                if result_id is None:
                    logger.error(f"НЕХВАТКА СВОБОДНЫХ КЛЮЧЕЙ В БАЗЕ ДАННЫХ : "
                                 f"Не удалось получить неиспользуемый ключ для сервера,  {server_id}")
                    await bot.send_message(err_send, "НЕХВАТКА СВОБОДНЫХ КЛЮЧЕЙ В БАЗЕ ДАННЫХ "
                                                     "проверь скрипт create_keys")

                    return False

                _key_id, _outline_id, _sever_id, _key_value, _used = result_id
                logger.info(
                    f"Куплен неиспользуемый ключ id : {_key_id} для пользователя: {user_id}, cервер {server_id}")
            except Exception as e:
                logger.error(
                    f'KEY_GET_ERROR Ошибка при получении ключа из БД id пользователя: {user_id}, {e}')
                await bot.send_message(err_send, f'KEY_GET_ERROR Ошибка при получении ключа из БД id пользователя: {user_id}, {e}')
                return False

            try:
                # меняем used с 0 на 1 у текущего ключа
                mycursor.execute(sql_update_key_used, [_outline_id])
            except Exception as e:
                logger.error(f'KEY_GET_ERROR Ошибка смены 0 на 1 у текущего ключа : {user_id}, {e}')

                return False

            try:
                # добавляем в таблицу user_keys приобретенный юзером ключ, + дата начала и конца действия ключа
                mycursor.execute(
                    sql_insert_user_key, (user_id,
                                          _key_id,
                                          key_name,
                                          start_date,
                                          stop_date)
                )
                logger.info(f"Добавлен ключ {_key_id},"
                            f"{key_name},"
                            f"юзер -  {user_id}")
            except Exception as e:
                logger.error(
                    f'KEY_GET_ERROR Ошибка добавления ключа в user_keys + '
                    f'дата начала и конца действия ключа : {user_id}, {e}')
                await bot.send_message(err_send, f'KEY_GET_ERROR Ошибка добавления ключа в user_keys + '
                    f'дата начала и конца действия ключа : {user_id}, {e}')

                return False

        return _key_id
    except Exception as e:
        logging.error(f'Произошла ошибка при добавлении ключа: {user_id}, ошибка :{e}')
        await bot.send_message(err_send, f'Произошла ошибка при добавлении ключа: {user_id}, ошибка :{e}')
        return False


# проверяем на повторность название сервера
def check_names(user_id, key_name):
    mydb = create_connection()

    if mydb is None:
        logger.error('Не удалось создать соединение с БД')
        return "Произошла ошибка, обратитесь к администратору или попробуйте еще раз"

    try:
        with mydb.cursor(buffered=True) as mycursor:
            mycursor.execute(sql_query_check_name, (user_id,))
            result = mycursor.fetchall()

        return (key_name,) in result
    except Exception as e:
        logger.error(f'Ошибка при проверке на повторяющиеся имена для user_id {user_id}: {e}')
        return False


def keys_to_send(key_data_amster,
                 key_data_german,
                 key_data_kz,
                 key_data_russia,
                 key_data_turkey,
                 ):
    lst_answer = []

    def country_text(name, key, date):
        text = f"""Название ключа <b>"{name}"</b>,\n - <code>{key}</code>\n(👆кликни для копирования)\n- ключ действителен до {date}\n\n"""

        return text

    if key_data_amster:
        amsterdam_keys_text = "🇳🇱<b>Ключи Нидерланды - Амстердам</b> :\n\n"
        for key, date, name in key_data_amster:
            formatted_date = date.strftime('%d %B %Y')
            amsterdam_keys_text += country_text(name, key, formatted_date)
        lst_answer.append(amsterdam_keys_text)

    if key_data_german:
        germany_keys_text = "🇩🇪<b>Ключи Германии - Франкфурт</b> :\n\n"
        for key, date, name in key_data_german:
            formatted_date = date.strftime('%d %B %Y')
            germany_keys_text += country_text(name, key, formatted_date)
        lst_answer.append(germany_keys_text)

    if key_data_kz:
        kz_keys_text = "🇰🇿<b>Ключи Казахстан - Алматы</b> :\n\n"
        for key, date, name in key_data_kz:
            formatted_date = date.strftime('%d %B %Y')
            kz_keys_text += country_text(name, key, formatted_date)
        lst_answer.append(kz_keys_text)

    if key_data_russia:
        russia_keys_text = "🇷🇺<b>Ключи Россия - СПБ</b> :\n\n"
        for key, date, name in key_data_russia:
            formatted_date = date.strftime('%d %B %Y')
            russia_keys_text += country_text(name, key, formatted_date)
        lst_answer.append(russia_keys_text)

    if key_data_turkey:
        turkey_keys_text = "🇹🇷<b>Ключи Турция - Стамбул</b> :\n\n"
        for key, date, name in key_data_turkey:
            formatted_date = date.strftime('%d %B %Y')
            turkey_keys_text += country_text(name, key, formatted_date)
        lst_answer.append(turkey_keys_text)

    if not key_data_amster and not key_data_german and not key_data_kz and not key_data_russia and not key_data_turkey:
        answer = f"""У вас нет ключей🙁
                \nЧтобы приобрести ключ доступа, нажмите <b>"Получить ключ"</b>"""
        return answer
    else:
        return lst_answer

# def chek_promo_name(name_promo):
#     now = datetime.datetime.now()
#     sql_query = f"""SELECT * FROM users WHERE promocode = '{name_promo}'"""
#     mydb = create_connection()
#     if mydb is None:
#         logger.error('Не удалось создать соединение с БД', now)
#         return "Произошла ошибка, обратитесь к администратору или попробуйте еще раз"
#
#     try:
#         with mydb.cursor(buffered=True) as mycursor:
#             # узнаем user_id юзера
#             mycursor.execute(sql_query)
#             result = mycursor.fetchone()
#
#         return result
#
#     except mysql.connector.errors as err:
#         logger.error(f'Произошла ошибка при поиске промокода : {name_promo}, время {now}',
#                      err)
#
#
# def chek_promo_telegram_id(telegram_id):
#     now = datetime.datetime.now()
#     sql_query = f"""SELECT promocode  FROM users WHERE telegram_id = {telegram_id}"""
#     mydb = create_connection()
#     if mydb is None:
#         logger.error('Не удалось создать соединение с БД', now)
#         return "Произошла ошибка, обратитесь к администратору или попробуйте еще раз"
#
#     try:
#         with mydb.cursor(buffered=True) as mycursor:
#             # узнаем user_id юзера
#             mycursor.execute(sql_query)
#             result = mycursor.fetchone()
#
#         return result
#
#     except mysql.connector.errors as err:
#         logger.error(f'Произошла ошибка при поиске промокода : {telegram_id}, время {now}',
#                      err)
#
#
# def save_promocode(telegram_id, name_promo):
#     now = datetime.datetime.now()
#     sql_query = f"""UPDATE users SET promocode = '{name_promo}' WHERE telegram_id = {telegram_id};"""
#
#     mydb = create_connection()
#     if mydb is None:
#         logger.error('Не удалось создать соединение с БД', now)
#         return "Произошла ошибка, обратитесь к администратору или попробуйте еще раз"
#
#     try:
#         with mydb.cursor(buffered=True) as mycursor:
#             # узнаем user_id юзера
#             mycursor.execute(sql_query)
#
#     except mysql.connector.Error as err:
#         logger.error(
#             f'Произошла ошибка при сохранении промокода : {name_promo}, у пользователя {telegram_id} время {now}',
#             err)
