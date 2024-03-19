import mysql.connector
from config import host, user, password, database
from logger import logger


def create_connection():
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            unix_socket='/tmp/mysql.sock',
            database=database,
            autocommit=True
        )

        # logger.info('DB_CONNECT_SUCCESS')
        return conn  # Возвращаем объект соединения
    except mysql.connector.errors.InterfaceError as err:
        logger.error(f'DB_CONNECT_ERROR: %s %s, ошибка - {err}')
        return None
