import mysql.connector
from get_conn import create_connection
import locale

from datetime import datetime, timedelta

from telebot_ import sync_send_message

from logger import logger
from config import err_send


# mydb = create_connection()
# mycursor = mydb.cursor()


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
def get_all_users():
    sql_get_users = "SELECT telegram_id FROM users"

    result = execute_query(sql_get_users)

    users = [value for _tuple in result for value in _tuple]

    return users


def get_users_not_trial_and_not_keys():
    sql_get_users_not_trial = "SELECT telegram_id FROM users " \
                              "WHERE user_id NOT IN (SELECT user_id FROM user_keys) " \
                              "AND free_tariff = 0;"

    result = execute_query(sql_get_users_not_trial)

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
            return False

    def update_last_activity(self, user_id):
        try:
            # обновляем last_seen в last_activity
            sql_update_act = "UPDATE users SET last_seen = %s WHERE user_id = %s"
            # ищем last_seen в last_activity
            sql_select_act = "SELECT last_seen FROM users WHERE user_id = %s"
            # если записей нет вообще то создаем

            now = datetime.now()

            resul_select = self.execute_query(sql_select_act, (user_id,))

            if resul_select:
                result_update = self.execute_query(sql_update_act, (now, user_id,))
                # logger.info(f"UPDATE LAST ACTIVITY user - {user_id}, {now}")
                return result_update
        except Exception as e:
            logger.error(f"ERROR:update_last_activity - ошибка при обновлении информации о последней"
                         f" активности пользователя - {user_id}, ошибка - {e}")
            return False

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

    def get_user_id_with_key_id(self, key_id):
        try:
            sql_get_user_id = " SELECT user_id FROM user_keys WHERE key_id = %s"
            result = self.execute_query(sql_get_user_id, (key_id,))
            if result:
                return result[0]
            else:
                return None
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_id_with_key_id - {e}")

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

    def get_userid_firsname_nickname(self, telegram_id):

        try:
            query = "SELECT user_id, username, nickname FROM users WHERE telegram_id = %s"

            result = self.execute_query(query, (telegram_id,))

            return result[0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_userid_firsname_nickname - {e}")
            return None

    def get_user_data(self, telegram_id):
        try:
            query = "SELECT * FROM users WHERE telegram_id = %s"
            result = self.execute_query(query, (telegram_id,))
            if not result:
                return None
            result = result[0]
            referer_telegram_id = result[3]
            if result[3]:
                referer_telegram_id = self.get_referrer_telegram_id(result[0])

            info = {
                'user_id': result[0],
                'first_name': result[1],
                'telegram_id': result[2],
                'referer_id': result[3],
                'free_tariff': result[4],
                'admin': result[5],
                'lastname': result[6],
                'username': result[7],
                'premium': result[8],
                'language': result[9],
                'date_accession': result[10],
                'last_seen': result[12],
                'referer_telegram_id': referer_telegram_id,
            }
            return info
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_data - {e}")
            return None

    def get_user_data2(self, user_id):
        try:
            query = "SELECT * FROM users WHERE user_id = %s"
            result = self.execute_query(query, (user_id,))
            if not result:
                return None
            result = result[0]
            referer_telegram_id = result[3]
            if result[3]:
                referer_telegram_id = self.get_referrer_telegram_id(result[0])
            info = {
                'user_id': result[0],
                'first_name': result[1],
                'telegram_id': result[2],
                'referer_id': result[3],
                'free_tariff': result[4],
                'admin': result[5],
                'lastname': result[6],
                'username': result[7],
                'premium': result[8],
                'language': result[9],
                'date_accession': result[10],
                'last_seen': result[12],
                'referer_telegram_id': referer_telegram_id,
            }
            return info
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_data - {e}")
            return None

    def get_user_info(self, user_id):
        try:
            user_info = self.get_user_data2(user_id)
            user_name = user_info.get("username")
            referral_balance = self.get_user_balance_bonus(user_id)
            count_referrals = self.count_referrals(user_id)
            referer_user_id = user_info.get('referer_id')
            referer_telegram_id = self.get_referrer_telegram_id(user_id)
            if referer_user_id is None:
                referer_user_id = 'Пусто'
                referer_telegram_id = 'Пусто'

            if self.free_tariff(user_id) == "USED":

                free_tariff = "Использован"
            else:
                free_tariff = "Не использован"

            all_info = (
                f"<b>user_id:</b> {user_id}\n"
                f"<b>Имя пользователя:</b> {user_name}\n"
                f"<b>Реферальный баланс:</b> {referral_balance}\n"
                f"<b>Количество рефералов:</b> {count_referrals}\n"
                f"<b>Реферер:</b> {referer_user_id}, {referer_telegram_id}\n"
                f"<b>Бесплатный тариф:</b> {free_tariff}\n\n")
            return all_info
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_info - {e}")

    def searche_user_id_with_user_name(self, user_name):

        try:
            query = """SELECT user_id FROM users WHERE nickname = %s"""

            result = self.execute_query(query, (user_name,))

            if result:
                return result[0][0]
            else:
                return None

        except Exception as e:
            logger.error(f"QUERY_ERROR - searche_with_usr_name - {e}")
            return None

    # получаем сервер_айди который использует юзер
    def get_current_used_server(self, key_id):
        try:
            query = """SELECT server_id FROM outline_keys WHERE key_id = %s"""

            return self.execute_query(query, (key_id,))
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_current_used_server - {e}")

    # получаем текущий баланс с прибыли рефералов
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
    def get_user_keys_info(self, user_id):
        try:
            sql = '''SELECT      u.key_id,     o.server_id,     o.key_value,     u.stop_date FROM     outline_keys o LEFT JOIN user_keys u ON     o.key_id = u.key_id WHERE     u.user_id = %s'''

            return self.execute_query(sql, (user_id,))

        except Exception as e:
            logger.error(f"QUERY_ERROR - get_user_keys_info - {e}")

    # берем все key_id  у юзера
    def get_keys_ids(self, user_id):
        try:
            query = """SELECT key_id FROM user_keys WHERE user_id = %s"""
            result = self.execute_query(query, (user_id,))
            if not result:
                return None
            return result
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_keys_ids - {e}")
            return None

    # узнаем кому принадлежит ключ
    def whose_key(self, key_id):
        try:
            query = """SELECT user_id FROM user_keys WHERE key_id = %s"""
            result = self.execute_query(query, (key_id,))
            if not result:
                return None
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - whose_key - {e}")
            return None

    # получаем все свободные server_id, которые могут быть использованы
    def get_used_server_id(self):
        try:
            query = """SELECT DISTINCT server_id FROM outline_keys WHERE used = 0"""

            result = self.execute_query(query, )
            return result
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_used_server_id - {e}")

    def get_count_free_keys(self):
        try:
            query = """SELECT COUNT(*) FROM users WHERE free_tariff = 1"""

            result = self.execute_query(query, )
            logger.info("QUERY - get_count_free_keys")
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_count_free_keys - {e}")

    def get_count_user_with_date(self, date):
        try:
            query = """SELECT COUNT(*) FROM users WHERE DATE(date_accession) = %s"""

            result = self.execute_query(query, (date,))
            logger.info("QUERY - get_count_user_with_date")
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_count_user_with_date - {e}")

    def get_count_all_keys(self):
        try:
            query = """SELECT COUNT(*) FROM user_keys"""

            result = self.execute_query(query, )
            logger.info("QUERY - get_count_free_keys")
            return result[0][0]
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_count_all_keys - {e}")

    # получаем список имен ключей
    def get_key_ids(self, user_id):
        query = """SELECT key_id FROM user_keys WHERE user_id = %s"""

        return self.execute_query(query, (user_id,))

    # количество рефералов
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

    # использует ли юзер бесплатный тариф, поиск по юзер_айди 1 0 или NONE
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

    def get_users_not_use_trial(self):
        sql = "SELECT telegram_id FROM users WHERE free_tariff = 0"
        try:
            result = self.execute_query(sql)
            list_telegram_id = []

            for tg in result:
                list_telegram_id.append(tg[0])
            return list_telegram_id
        except Exception as e:
            logger.error(f"QUERY_ERROR - get_users_not_use_trial - {e}")
            return None

    # использует ли юзер бесплатный тариф, поиск по telegram_id
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
                                WHERE used = 0 AND server_id IN (1, 2, 6, 4, 5)
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


def if_new_user(telegram_id, username, referer_user_id, last_name, nickname, language, premium):
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
                    sql_insert_user = "INSERT INTO users " \
                                      "(username, telegram_id, referer_id, lastname, nickname, premium, language)" \
                                      " VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    mycursor.execute(sql_insert_user, (username, telegram_id, referer_user_id,
                                                       last_name, nickname, premium, language))

                    user_id = mycursor.lastrowid

                    logger.info(f"NEW USER : добавлен в базу {telegram_id}, {username}, referer - {referer_user_id}")
                else:
                    # Добавляем нового пользователя без refer_id
                    sql_insert_user = "INSERT INTO users " \
                                      "(username, telegram_id, lastname, nickname, premium, language)" \
                                      " VALUES (%s, %s, %s, %s, %s, %s)"
                    mycursor.execute(sql_insert_user, (username, telegram_id, last_name,
                                                       nickname, premium, language))
                    user_id = mycursor.lastrowid

                    logger.info(f"NEW USER : добавлен в базу {telegram_id}, {username} - referer - None")
                return user_id
    except Exception as e:
        logger.error(f"ERROR:if_new_user - Ошибка базы данных: {e}")
        sync_send_message(err_send, f"ERROR:if_new_user - Ошибка базы данных: {e}")
        return None
