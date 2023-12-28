import outline_api

from get_conn import create_connection

from config import *

from telebot_ import sync_send_message
from user_data import execute_query

from logger import logger

# mydb = create_connection()
#
# cursor = mydb.cursor()

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
        result = execute_query(query_templates['search_server_id_with_key_id'], (key_id,))
        logger.info(f"server_id найден {result[0][0]}")
        return result[0][0]
    except Exception as e:
        logger.error(f"Ошибка при поиске сервера , {e}")
        return None


def delete_from_manager(key_ids, outline_keys):
    try:
        success = True  # Флаг для отслеживания успеха удаления всех ключей
        for key_id, outline_key in zip(key_ids, outline_keys):
            server_id = get_server_id(key_id)

            # print(server_id)
            if server_id:
                manager = managers.get(server_id)
                try:
                    manager.delete(outline_key)
                    logger.info(f"DELETE_KEYS_FROM_MANAGER - ключ - {key_id} удален успешно из менеджера")
                except outline_api.errors.DoesNotExistError as dne_error:
                    # Обработка исключения, когда ключ не существует
                    error = f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка, ключ {key_id} не существует: {dne_error}"
                    sync_send_message(err_send, error)
                    logger.error(error)
                except Exception as e:
                    # Обработка других исключений
                    logger.error(
                        f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка при удалении ключа {key_id} из outline manager, ошибка - {e}")
                    success = False  # Устанавливаем флаг в False в случае ошибки
                    continue
            else:
                logger.error(f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка, сервер для ключа {key_id} не найден")
                success = False  # Устанавливаем флаг в False в случае отсутствия сервера

        return success

    except Exception as e:
        # Обработка других исключений
        error = f"ERROR:DELETE_KEYS_FROM_MANAGER - Произошла ошибка при удалении ключей " \
                f"{outline_keys} из outline manager, ERROR - {e}"
        logger.error(error)
        sync_send_message(err_send, error)
        return False
