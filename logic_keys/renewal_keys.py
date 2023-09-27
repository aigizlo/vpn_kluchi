from db_conn.get_conn import create_connection
from logs.logger import logger

from user_data import UserData

user_data = UserData()

sql_search_key_id = """SELECT user_keys.key_id FROM users 
                            JOIN user_keys ON users.user_id = user_keys.user_id 
                                WHERE users.user_id = %s AND user_keys.name = %s"""

sql_update_date_work_key = """UPDATE user_keys 
                                SET stop_date = stop_date + INTERVAL %s 
                                    MONTH WHERE key_id = %s"""

answer_if_update_date = f"""Ваш ключ  успешно продлен на указанный срок, перейдите в раздел "Мои ключи" """

answer_if_not_update_date = f"Произошла ошибка при продлении ключа. " \
                            f"Пожалуйста, попробуйте еще раз или свяжитесь с поддержкой."

logger_template = {
    "info": "Продлен ключ id : {key_id} для пользователя: {user_id}, на {month}, месяцев",

    "error": """Ошибка при продлении ключа id : {key_id} для пользователя: {user_id}, "
                   на {month}, месяцев. Ошибка: {e}"""

}


# продлеваем ключ, по telegram_id, key_name (название ключа), month - месяц
def renewal_keys(user_id, key_name, month):

    try:
        # подключаемся к базе
        with create_connection() as mydb, mydb.cursor(buffered=True) as mycursor:
            # запрос для поиска ключа (key_id) в базе данных по user_id и названию ключа (key_name)
            mycursor.execute(sql_search_key_id, (user_id, key_name))
            result_id = mycursor.fetchone()

            if result_id:
                key_id = result_id[0]

                # продлеваем данный ключ на указанный month (обновляем дату работы ключа)
                mycursor.execute(sql_update_date_work_key, (month, key_id))
                logger.info(logger_template["info"].format(key_id=key_id, user_id=user_id, month=month))
                return True

    except Exception as e:
        logger.error(logger_template["error"].format(key_id=key_id, user_id=user_id, month=month, e=e))
        return False
