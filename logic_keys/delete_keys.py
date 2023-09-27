import logging

import outline_api

from db_conn.get_conn import create_connection

from config import *

from outline_api import Manager  # Импорт вашего класса Manager

from user_data import execute_query

from logs.logger import logger

mydb = create_connection()

cursor = mydb.cursor()

# Конфигурация логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

manager_amsterdam = Manager(apiurl=apiurl_amsterdam, apicrt=apicrt_amsterdam)

manager_germany = Manager(apiurl=apiurl_germany, apicrt=apicrt_germany)

manager_kz = Manager(apiurl=apiurl_kz, apicrt=apicrt_kz)

manager_spb = Manager(apiurl=apiurl_spb, apicrt=apicrt_spb)

manager_turkey = Manager(apiurl=apiurl_turkey, apicrt=apicrt_turkey)

managers = {
    1: manager_amsterdam,
    2: manager_germany,
    3: manager_kz,
    4: manager_spb,
    5: manager_turkey
}

query_templates = {
    'delete_user_keys': """DELETE FROM user_keys 
                                WHERE key_id IN (%s)""",

    'delete_outline_keys': """DELETE FROM outline_keys 
                                WHERE key_id IN (%s)""",

    'search_server_id_with_outline_key_id': """SELECT server_id FROM outline_keys 
                                                WHERE outline_key_id = (%s)""",

    'search_server_id_with_key_id': """SELECT server_id FROM outline_keys 
                                                WHERE key_id = (%s)"""
}


def delete_keys(key_ids):  # key_ids удаляем из базы и
    # Удаление ключей из базы данных user_keys
    placeholders = ", ".join(["%s"] * len(key_ids))

    # запросы для удаления ключей, берем из шаблона
    query_user_keys = query_templates["delete_user_keys"] % placeholders
    query_outline_keys = query_templates["delete_outline_keys"] % placeholders

    try:
        execute_query(query_user_keys, key_ids)
        logger.info(
            f"DELETE_KEYS_FROM_USER_KEYS: - Удаление ключей {key_ids}  из бд user_keys данных прошло успешно , ")
    except Exception as e:
        logger.error(
            f"ERROR:DELETE_KEYS_FROM_USER_KEYS - Не удалось удалить ключи {key_ids} в бд user_keys, ,ошибка -  {e}")

    try:
        execute_query(query_outline_keys, key_ids)
        logger.info(f"DELETE_KEYS_FROM_OUTLINE_KEYS - Удаление ключей {key_ids} из бд outline_keys данных прошло "
                    f"успешно,")
    except Exception as e:
        logger.error(
            f"ERROR:DELETE_KEYS_FROM_OUTLINE_KEYS - Не удалось удалить ключи {key_ids} в бд outline_keys:, "
            f"ошибка - {e}")


def get_server_id(key_id):  # ищем server_id по key_id
    try:
        execute_query(query_templates['search_server_id_with_key_id'], (key_id,))
        result = cursor.fetchone()
        return result[0][0]
        logger.info(f"server_id найден {result[0][0]}")
    except Exception as e:
        logger.error(f"Ошибка при поиске сервера , {e}")
        return None


async def delete_from_manager(key_ids, outline_keys):
    try:
        success = True  # Флаг для отслеживания успеха удаления всех ключей
        for key_id, outline_key in zip(key_ids, outline_keys):
            server_id = get_server_id(key_id)
            if server_id:
                manager = managers.get(server_id)
                try:
                    manager.delete(outline_key)
                    logger.info(f"DELETE_KEYS_FROM_MANAGER - ключ - {key_id} удален успешно из менеджера")
                except outline_api.errors.DoesNotExistError as dne_error:
                    # Обработка исключения, когда ключ не существует
                    await bot.send_message(err_send,
                        f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка, ключ {key_id} не существует: {dne_error}")
                    logger.error(
                        f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка, ключ {key_id} не существует: {dne_error}")
                except Exception as e:
                    # Обработка других исключений
                    logger.error(
                        f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка при удалении ключа {key_id} из outline manager, ошибка - {e}")
                    success = False  # Устанавливаем флаг в False в случае ошибки
                    continue
            else:
                logger.error(f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка, сервер для ключа {key_id} не найден")
                success = False  # Устанавливаем флаг в False в случае отсутствия сервера

        return success  # Возвращаем флаг успеха после завершения цикла

    except Exception as e:
        # Обработка других исключений
        logger.error(
            f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка при удалении ключей {outline_keys} из outline "
            f"manager, ERROR - {e}")
        await bot.send_message(err_send,
            f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка при удалении ключей {outline_keys} из outline "
            f"manager, ERROR - {e}")
        return False
