import mysql.connector
from db_conn.get_conn import create_connection
import locale

from logs.logger import logger
from config import err_send, bot

mydb = create_connection()
mycursor = mydb.cursor()


class QueryExecutionError(Exception):
    pass


def execute_query(query, params=None):
    try:
        with create_connection() as mydb:
            with mydb.cursor() as mycursor:
                if params:
                    mycursor.execute(query, params)
                else:
                    mycursor.execute(query)
                return mycursor.fetchall()
    except Exception as e:
        logger.error(f"PROCESS:execute_query, запрос {query}, {params}.  Ошибка - {e}")

        raise QueryExecutionError(f"Ошибка при выполнении запроса : {query},Error -  {e}")


def get_list_admins_telegram_id():
    sql_query = "SELECT telegram_id FROM users WHERE admin = 1"
    result = execute_query(sql_query)
    # Преобразовываем кортежи в int значения
    telegram_ids = [entry[0] for entry in result]

    return telegram_ids


# используем для получения всех tg_id пользователей
async def get_all_users():
    sql_get_users = "SELECT telegram_id FROM users"

    result = execute_query(sql_get_users)

    users = [value for _tuple in result for value in _tuple]

    return users


class UserData:

    def __init__(self):
        self.connection = create_connection()
        self.cursor = self.connection.cursor()

    def __enter__(self):
        self.connection = create_connection()
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def execute_query(self, query, args=None):
        try:
            if not self.connection.is_connected():
                self.connection.reconnect()
            self.cursor.execute(query, args)
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            logger.error(f"QUERY_ERROR - {e}")

    def get_tg_if_use_user_id(self, user_id):
        try:
            sql_get_tg_id = "SELECT telegram_id FROM users WHERE user_id = %s "
            result = self.execute_query(sql_get_tg_id, (user_id,))
            if result:
                return result[0][0]
            else:
                return None
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_tg_if_use_user_id - {e}")

    def get_user_name(self, user_id):
        try:
            query = "SELECT username FROM users WHERE user_id = %s"
            result = self.execute_query(query, (user_id,))
            if result:
                return result[0][0]
            else:
                return None
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_name - {e}")

    def get_user_info(self, user_id):
        try:
            user_name = self.get_user_name(user_id)
            print(user_name)
            balance = self.get_user_balance_ops_by_user_id(user_id)
            print(balance)
            referl_balance = self.get_user_balance_bonus(user_id)
            print(referl_balance)
            count_referrals = self.count_referrals(user_id)
            print(count_referrals)
            referer_user_id = self.get_referrer_user_id(user_id)
            print(referer_user_id)
            referer_telegram_id = self.get_referrer_telegram_id(user_id)
            print(referer_telegram_id)

            if self.free_tariff(user_id) == "USED":

                free_tariff = "Использован"
            else:
                free_tariff = "Не использован"

            all_info = (
                f"<b>Имя пользователя:</b> {user_name}\n"
                f"<b>Баланс пользователя:</b> {balance}\n"
                f"<b>Реферальный баланс:</b> {referl_balance}\n"
                f"<b>Количество рефералов:</b> {count_referrals}\n"
                f"<b>Реферер:</b> {referer_user_id}, {referer_telegram_id}\n"
                f"<b>Бесплатный тариф:</b> {free_tariff}\n\n"
                "<b>Ключи:</b>\n\n")

            return all_info
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_info - {e}")

    # user_id по его телеграм айди
    def get_user_id(self, telegram_id):
        try:
            query = "SELECT user_id FROM users WHERE telegram_id = %s"
            result = self.execute_query(query, (telegram_id,))
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_id - {e}")
            return None

    # получаем текущий баланс
    def get_user_balance_ops_by_user_id(self, user_id):
        try:
            query = f"""
                    SELECT SUM(amount) AS addmoney_balance
                    FROM user_balance_ops
                    WHERE user_id = %s AND optype = 'addmoney'
                    """
            result = self.execute_query(query, (user_id,))
            cur_balance = result[0][0]

            if not cur_balance:
                return 0
            return cur_balance
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_balance_ops_by_user_id - {e}")

    # получаем текущий баланс c рефералов
    def get_user_balance_bonus(self, user_id):
        try:
            query = f"""
                        SELECT SUM(amount) AS bonus_balance
                        FROM user_balance_ops
                        WHERE user_id = %s AND optype = 'bonus';
                    """
            result = self.execute_query(query, (user_id,))
            if not result[0][0]:
                return 0
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_balance_bonus - {e}")

    # список ключей юзера
    def get_user_keys(self, user_id):

        locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        key_data_amster = self.get_keys(user_id, 1) if self.get_keys(user_id, 1) else None
        key_data_german = self.get_keys(user_id, 2) if self.get_keys(user_id, 2) else None
        key_data_kz = self.get_keys(user_id, 3) if self.get_keys(user_id, 3) else None
        key_data_russia = self.get_keys(user_id, 4) if self.get_keys(user_id, 4) else None
        key_data_turkey = self.get_keys(user_id, 5) if self.get_keys(user_id, 5) else None

        lst = []
        lst.extend([key_data_amster, key_data_german, key_data_kz, key_data_russia, key_data_turkey])
        return lst

    def get_keys(self, user_id, server_id):
        try:
            query = """SELECT ok.key_value, uk.stop_date, uk.name 
                    FROM outline_keys ok JOIN user_keys uk ON ok.key_id = uk.key_id 
                    WHERE uk.user_id = %s AND ok.server_id = %s"""

            return self.execute_query(query, (user_id, server_id,))
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_keys - {e}")

    # получаем список имен ключей
    def get_user_name_keys(self, user_id):
        # запрос для получени ключа, имени ключа, даты окончания сервер 1
        query = """SELECT uk.name FROM outline_keys ok 
                JOIN user_keys uk ON ok.key_id = uk.key_id 
                WHERE uk.user_id = %s"""

        return self.execute_query(query, (user_id,))

    def count_referrals(self, user_id):
        query = """SELECT COUNT(*) FROM users WHERE referer_id = %s"""
        try:
            result = self.execute_query(query, (user_id,))
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - count_referrals - {e}")

    def get_referrer_user_id(self, user_id):
        query = """SELECT referer_id FROM users WHERE user_id = %s"""
        try:
            result = self.execute_query(query, (user_id,))
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_referrer_user_id - {e}")

    def get_referrer_telegram_id(self, user_id):
        try:
            referrer_user_id = self.get_referrer_user_id(user_id)
            if referrer_user_id is None:
                return None
            else:
                result = self.execute_query("SELECT telegram_id FROM users WHERE user_id = %s", (referrer_user_id,))
                return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_referrer_telegram_id - {e}")

    # использует ли юзер бесплатный тариф,поиск по юзер_айди 1 0 или NONE
    def free_tariff(self, user_id):
        query = "SELECT free_tariff FROM users WHERE user_id = %s"
        try:
            result = self.execute_query(query, (user_id,))
            if result[0][0] == 0:
                return "UNUSED"
            if result[0][0] == 1:
                return "USED"
        except Exception as e:
            logger.error(f"QUERY_ERROR - free_tariff - {e}")
            return None

    # использует ли юзер бесплатный тариф,поиск по telegram_id
    def free_tariff_tg(self, telegram_id):
        query = "SELECT free_tariff FROM users WHERE telegram_id = %s"
        try:
            result = self.execute_query(query, (telegram_id,))
            if result[0][0] == 0:
                return "UNUSED"
            if result[0][0] == 1:
                return "USED"
        except Exception as e:
            logger.error(f"QUERY_ERROR - free_tariff_tg - {e}")
            return None

    # смена статуса бесплатного тарифного плана с 0 на 1
    def change_free_tariff(self, user_id, status):
        sql_used_free_tariff = "UPDATE users SET free_tariff = %s WHERE user_id = %s"
        try:
            result = self.execute_query(sql_used_free_tariff, (status, user_id,))
            return result

        except Exception as e:
            logger.error(f"QUERY_ERROR - change_free_tariff - {e}")
            return None

    # получаем конкретный ключ
    def get_key_value(self, key_id):
        sql_get_key = "SELECT key_value FROM outline_keys WHERE key_id = %s"
        try:
            result = self.execute_query(sql_get_key, (key_id,))
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_key_value - {e}")
            return None

    # узнаем количество свободных ключей для всех серверов
    def count_free_keys(self):
        query = """SELECT server_id, COUNT(*) AS count 
                                FROM outline_keys
                                WHERE used = 0 AND server_id IN (1, 2, 3, 4, 5)
                                GROUP BY server_id"""
        try:
            result = self.execute_query(query)
            result_str = ", ".join(f"{server_id} - {count}" for server_id, count in result)
            return result_str
        except Exception as e:
            logger.error(f"QUERY_ERROR - count_free_keys - {e}")

    def all_users(self):
        try:
            result = self.execute_query("""SELECT COUNT(*) FROM users;""")
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - all_users - {e}")

    def close(self):
        self.cursor.close()
        self.connection.close()


def check_user_in_system(telegram_id):
    try:
        with create_connection() as mydb:
            with mydb.cursor() as mycursor:
                sql_check_new_user = "SELECT * FROM users WHERE telegram_id = %s"
                mycursor.execute(sql_check_new_user, (telegram_id,))
                result = mycursor.fetchone()
                if not result:
                    return result
                return True
    except Exception as e:
        logger.error(f"ERROR:check_user_in_system - Ошибка базы данных: {e}")


async def if_new_user(telegram_id, username, referer_user_id):
    try:
        # Создаем соединение с базой данных
        with create_connection() as mydb:
            with mydb.cursor() as mycursor:
                # Проверяем наличие пользователя по telegram_id
                sql_check_new_user = "SELECT * FROM users WHERE telegram_id = %s"
                mycursor.execute(sql_check_new_user, (telegram_id,))

                result = mycursor.fetchone()

                # Если пользователь уже существует, возвращаем False
                if result:
                    return False

                # Если указан referer_id, проверяем его наличие в базе данных
                if referer_user_id:
                    sql_check_referer = "SELECT * FROM users WHERE user_id = %s"
                    mycursor.execute(sql_check_referer, (referer_user_id,))
                    referer_result = mycursor.fetchone()
                    logger.info(f"NEW USER : {telegram_id}, {username}, referer - None")

                    # Если referer_id не найден, даем None
                    if not referer_result:
                        logger.info(f"PROCESS : if_new_user - несуществующий referer {telegram_id}, {username}")
                        referer_user_id = None

                    # Добавляем нового пользователя с указанным refer_id
                    sql_insert_user = "INSERT INTO users (username, telegram_id, referer_id) VALUES (%s, %s, %s)"
                    mycursor.execute(sql_insert_user, (username, telegram_id, referer_user_id,))
                    logger.info(f"NEW USER : добавлен в базу {telegram_id}, {username}, referer - {referer_user_id}")
                else:
                    # Добавляем нового пользователя без refer_id
                    sql_insert_user = "INSERT INTO users (username, telegram_id) VALUES (%s, %s)"
                    mycursor.execute(sql_insert_user, (username, telegram_id,))
                    logger.info(f"NEW USER : добавлен в базу {telegram_id}, {username} - referer - None")
                return True
    except Exception as e:
        logger.error(f"ERROR:if_new_user - Ошибка базы данных: {e}")
        await bot.send_message(err_send, f"ERROR:if_new_user - Ошибка базы данных: {e}")
        return None
