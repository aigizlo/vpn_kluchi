import logging
import random

from telebot_ import sync_send_message

from config import err_send, managers
from get_conn import create_connection
import datetime
from logger import logger
from user_data import execute_query

# SQL-запросы

sql_get_server_id = '''SELECT server_id FROM outline_keys WHERE outline_key_id = %s'''

sql_delete_from_bd = "DELETE FROM outline_keys WHERE outline_key_id = %s"

sql_delete_from_bd2 = "DELETE FROM user_keys WHERE key_id = %s"


sql_set_new_key_id = "UPDATE user_keys SET key_id = %s WHERE key_id = %s"

sql_get_outline_key_id = "SELECT outline_key_id FROM outline_keys WHERE key_id = %s"

sql_query_check_name = """SELECT user_keys.name FROM 
                            users JOIN user_keys ON users.user_id = user_keys.user_id 
                                WHERE users.user_id = %s"""

sql_select_user_id = "SELECT user_id FROM users WHERE user_id = %s"

sql_select_unused_key = "SELECT * FROM outline_keys WHERE used = 0 AND server_id = %s"

sql_update_key_used = "UPDATE outline_keys SET used = 1 WHERE outline_key_id = %s AND used = 0 AND server_id = %s"

sql_insert_user_key = """INSERT INTO user_keys (user_id, key_id, start_date, stop_date)
                           VALUES (%s, %s, %s, %s)"""

server_id_country_for_txt = {
    1: "🇩🇪<b>Ключи Германии - Франкфурт</b> :\n\n",
    2: "🇺🇸<b>Ключи Америка - Лос Анджелес</b> :\n\n"
}


def get_minimum_used_server():
    sql = """SELECT server_id FROM outline_keys GROUP BY server_id HAVING SUM(used = 1) <= 1"""
    sql2 = "SELECT DISTINCT server_id FROM outline_keys"
    result = execute_query(sql)
    if not result:
        result2 = execute_query(sql2)

        return random.choice(result2)[0]

    return result[0][0]


def add_keys(user_id, days):
    server_id = get_minimum_used_server()
    logger.info(f"get_minimum_used_server - {server_id}")
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
                    logger.error(f"NOT_FREE_KEYS НЕХВАТКА СВОБОДНЫХ КЛЮЧЕЙ В БАЗЕ ДАННЫХ : "
                                 f"Не удалось получить неиспользуемый ключ для сервера,  {server_id}")
                    sync_send_message(err_send, "NOT_FREE_KEYS НЕХВАТКА СВОБОДНЫХ КЛЮЧЕЙ В БАЗЕ ДАННЫХ "
                                                "проверь скрипт create_keys")

                    return False

                _key_id, _outline_id, _server_id, _key_value, _used = result_id
                logger.info(
                    f"GET_NEW_KEY Куплен неиспользуемый ключ id : {_key_id} для пользователя: {user_id}, сервер {server_id}")
            except Exception as e:
                logger.error(
                    f'GET_NEW_KEY_ERROR Ошибка при получении ключа из БД id пользователя: {user_id}, {e}')
                sync_send_message(err_send,
                                  f'GET_NEW_KEY_ERROR Ошибка при получении ключа из БД id пользователя: {user_id}, {e}')
                return False

            try:
                # меняем used с 0 на 1 у текущего ключа
                mycursor.execute(sql_update_key_used, (_outline_id, server_id,))
            except Exception as e:
                logger.error(f'GET_NEW_KEY_ERROR Ошибка смены 0 на 1 у текущего ключа : {user_id}, {e}')

                return False

            try:
                # добавляем в таблицу user_keys приобретенный юзером ключ, + дата начала и конца действия ключа
                mycursor.execute(
                    sql_insert_user_key, (user_id,
                                          _key_id,
                                          start_date,
                                          stop_date)
                )
                logger.info(f"Добавлен ключ {_key_id},"
                            f"юзер -  {user_id}")
            except Exception as e:
                logger.error(
                    f'Ошибка добавления ключа в user_keys + '
                    f'дата начала и конца действия ключа : user_id - {user_id}, {e}')
                sync_send_message(err_send, f'Ошибка добавления ключа в user_keys + '
                                            f'дата начала и конца действия ключа : {user_id}, {e}')

                return False

        return _key_id, _key_value, _server_id
    except Exception as e:
        logging.error(f'GET_NEW_KEY_ERROR:Произошла ошибка при добавлении ключа: {user_id}, ошибка :{e}')
        sync_send_message(err_send, f'GET_NEW_KEY_ERROR:Произошла ошибка при добавлении ключа: {user_id}, ошибка :{e}')
        return False


def add_free_keys(user_id):
    days = 10
    mydb = create_connection()
    server_id = get_minimum_used_server()

    # сроки работы ключа
    start_date = datetime.datetime.now()
    stop_date = start_date + datetime.timedelta(days=days)

    try:
        with mydb.cursor(buffered=True) as mycursor:
            try:
                logger.info('обращаемся к бд, чтобы взять неиспользуемый ключ')
                # обращаемся к бд, чтобы взять неиспользуемый ключ
                mycursor.execute(sql_select_unused_key, (server_id,))
                result_id = mycursor.fetchone()

                if result_id is None:
                    logger.error(f"НЕХВАТКА СВОБОДНЫХ КЛЮЧЕЙ В БАЗЕ ДАННЫХ : "
                                 f"Не удалось получить неиспользуемый ключ для сервера,  {server_id}")
                    sync_send_message(err_send, "НЕХВАТКА СВОБОДНЫХ КЛЮЧЕЙ В БАЗЕ ДАННЫХ "
                                                "проверь скрипт create_keys")

                    return False

                _key_id, _outline_id, _server_id, _key_value, _used = result_id
                logger.info(
                    f"GET_TRIAL_KEY id : {_key_id} для пользователя: {user_id}, сервер {server_id}")
            except Exception as e:
                logger.error(
                    f'GET_TRIAL_KEY_ERROR Ошибка при получении бесплатного ключа из БД id пользователя: {user_id}, {e}')
                sync_send_message(err_send,
                                  f'GET_TRIAL_KEY Ошибка при получении бесплатного ключа из БД id пользователя: {user_id}, {e}')
                return False

            try:
                # меняем used с 0 на 1 у текущего ключа
                mycursor.execute(sql_update_key_used, (_outline_id, server_id,))
            except Exception as e:
                logger.error(f'GET_TRIAL_KEY Ошибка смены 0 на 1 у текущего ключа : {user_id}, {e}')

                return False

            try:
                # добавляем в таблицу user_keys приобретенный юзером ключ, + дата начала и конца действия ключа
                mycursor.execute(
                    sql_insert_user_key, (user_id,
                                          _key_id,
                                          start_date,
                                          stop_date)
                )
                logger.info(f"Добавлен ключ {_key_id},"
                            f"юзер -  {user_id}")
            except Exception as e:
                logger.error(
                    f'GET_TRIAL_KEY_ERROR Ошибка добавления бесплатного ключа в user_keys + '
                    f'дата начала и конца действия ключа : user_id - {user_id}, {e}')
                sync_send_message(err_send, f'GET_TRIAL_KEY_ERROR Ошибка добавления бесплатного ключа в user_keys + '
                                            f'дата начала и конца действия ключа : {user_id}, {e}')

                return False

        return _key_value, _server_id
    except Exception as e:
        logging.error(f'GET_TRIAL_KEY_ERROR Произошла ошибка при добавлении бесплатного ключа: {user_id}, ошибка :{e}')
        sync_send_message(err_send, f'Произошла ошибка при добавлении бесплатного ключа: {user_id}, ошибка :{e}')
        return False


def keys_send(keys_lst):
    txt = ''

    unic_server_id = 0

    def text(key_id, key, date):
        text = f"""<b>Ключ № {key_id}</b> - действителен до {date}\n\n👇(кликни для копирования)\n<code>{key}</code>\n\n"""

        return text

    def country_text(server_id, key_id, key, date):
        txt = server_id_country_for_txt.get(server_id)

        text = f"""<b>Ключ № {key_id}</b> - действителен до {date}\n\n👇(кликни для копирования)\n<code>{key}</code>\n\n"""

        return txt + text

    for key_data in keys_lst:
        key_id = key_data[0]
        server_id = key_data[1]
        key_value = key_data[2]
        key_date = key_data[3].strftime('%d %B %Y')

        if unic_server_id == server_id:
            txt += text(key_id, key_value, key_date)
        else:
            txt += country_text(server_id, key_id, key_value, key_date)
            unic_server_id = server_id

    return txt


def exchange_server(key_id, server_id):
    mydb = create_connection()
    try:
        with mydb.cursor(buffered=True) as mycursor:
            try:
                logger.info('обращаемся к бд, чтобы взять неиспользуемый ключ')
                # обращаемся к бд, чтобы взять неиспользуемый ключ
                mycursor.execute(sql_select_unused_key, (server_id,))
                result_id = mycursor.fetchone()

                if result_id is None:
                    logger.error(f"НЕХВАТКА СВОБОДНЫХ КЛЮЧЕЙ В БАЗЕ ДАННЫХ : "
                                 f"Не удалось получить неиспользуемый ключ для сервера,  {server_id}")
                    sync_send_message(err_send, "НЕХВАТКА СВОБОДНЫХ КЛЮЧЕЙ В БАЗЕ ДАННЫХ "
                                                "проверь скрипт create_keys")

                    return False

                _key_id, _outline_id, _sever_id, _key_value, _used = result_id

                logger.info(
                    f"Взят неиспользуемый клюя для смены локации ключ id : {_key_id}, сервер {server_id}")
            except Exception as e:
                logger.error(
                    f'KEY_GET_ERROR Ошибка при получении ключа из БД , {e}')
                sync_send_message(err_send,
                                  f'KEY_GET_ERROR Ошибка при получении ключа из БД {e}')
                return False

            # вносим новый key_id
            execute_query(sql_set_new_key_id, (_key_id, key_id,))
            # меняем used с 0 на 1 у текущего нового ключа
            mycursor.execute(sql_update_key_used, (_outline_id, server_id,))

            # получаем outline_key_id старого ключа
            outline_key_id = execute_query(sql_get_outline_key_id, (key_id,))

            server_id = execute_query(sql_get_server_id, (outline_key_id[0][0],))

            manager = managers.get(server_id[0][0])
            try:
                manager.delete(outline_key_id[0][0])
                logger.info(f"DELETE_KEYS_FROM_MANAGER - ключ - {key_id} удален успешно из менеджера")
            except Exception as e:
                # Обработка других исключений
                logger.error(
                    f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка при удалении ключа {key_id} из outline manager, ошибка - {e}")
            try:
                execute_query(sql_delete_from_bd, (outline_key_id[0]))
            except Exception as e:
                # Обработка других исключений
                logger.error(
                    f"ERROR:DELETE_KEYS_FROM_DB - Произошла ошибка при удалении ключа {key_id} из outline_keys, ошибка - {e}")

        return _key_value

    except Exception as e:

        logger.error(f"Ошибка при смене ключа - {e}")

        return False


def delete_key(key_id):
    mydb = create_connection()
    try:
        with mydb.cursor(buffered=True) as mycursor:

            # получаем outline_key_id  ключа
            outline_key_id = execute_query(sql_get_outline_key_id, (key_id,))

            server_id = execute_query(sql_get_server_id, (outline_key_id[0][0],))

            manager = managers.get(server_id[0][0])
            try:
                manager.delete(outline_key_id[0][0])
                logger.info(f"DELETE_KEYS_FROM_MANAGER - ключ - {key_id} удален успешно из менеджера")
            except Exception as e:
                # Обработка других исключений
                logger.error(
                    f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка при удалении ключа {key_id} из outline manager, ошибка - {e}")
            try:
                execute_query(sql_delete_from_bd, (outline_key_id[0]))
                execute_query(sql_delete_from_bd2, (key_id,))

            except Exception as e:
                # Обработка других исключений
                logger.error(
                    f"ERROR:DELETE_KEYS_FROM_DB - Произошла ошибка при удалении ключа {key_id} из outline_keys, ошибка - {e}")
                return False
        return True

    except Exception as e:

        logger.error(f"Ошибка при удалении ключа - {e}")

        return False

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
