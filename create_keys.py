from time import sleep
from logger import logger
from telebot_ import sync_send_message

from get_conn import create_connection

from config import *

# номера серверов
germany_server = 1
usa_server = 2

servers_ids = [germany_server, usa_server]


# проверка на кол-во ключей по сервер_айди
def ChekCountKeys(server_id):
    try:
        with create_connection() as mydb:
            with mydb.cursor() as mycursor:
                mycursor.execute("SELECT COUNT(*) FROM outline_keys WHERE used = 0 AND server_id = %s", (server_id,))
                result = mycursor.fetchone()
                # logger.info(f"{result} количество свободных ключей на сервере {server_id}")

                if result[0] < 30:
                    # если количество меньше 30, то запускаем функцию по созданию
                    create_keys_servers(result[0], server_id)

    except Exception as e:
        # Обработка исключения, например, вывод сообщения об ошибке и логирование.
        logger.error(f"Ошибка при выполнении запроса: {e}")
        sync_send_message(f"ERROR:create_keys_servers - {e}")


def create_keys_servers(keys, server_id):
    logger.info(f"START:create_keys_servers")

    # Устанавиливаем менеджер(outline_api)
    _manager = managers.get(server_id)
    # выясняем сколько нужно создать
    generate = 30 - keys
    # Создание ключа
    try:
        with create_connection() as mydb:
            with mydb.cursor() as mycursor:
                for _ in range(generate):
                    new_key = _manager.new()
                    if new_key:
                        mycursor = mydb.cursor()
                        mycursor.execute(
                            "INSERT INTO outline_keys (outline_key_id, server_id, key_value, used) VALUES (%s, %s, "
                            "%s, %s)",

                            (new_key['id'], server_id, new_key['accessUrl'], 0))
                        logger.info(
                            f"create_keys_servers : добавлен ключ - {new_key['accessUrl']}, сервер - {server_id}")

    except Exception as e:
        logger.error(f"ERROR:create_keys_servers - {e}")
        sync_send_message(f"ERROR:create_keys_servers - {e}")


def run_create_keys():
    for server in servers_ids:
        ChekCountKeys(server)
        sleep(2)


if __name__ == '__main__':

    while True:
        run_create_keys()
        sleep(5)
