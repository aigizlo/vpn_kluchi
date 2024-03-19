from time import sleep
from telebot_ import sync_send_message, generate_prolong_button, sync_send_photo, main_menu_telebot
from logger import logger
from config import err_send, file_ids

from logic_keys.delete_keys import delete_keys, delete_from_manager

from user_data import execute_query

# запрос для получения ключей которые скоро истекут
sql_get_expired_keys = """
    SELECT u.telegram_id, uk.key_id, ok.key_value, ok.outline_key_id, s.country
    FROM user_keys uk     JOIN users u ON u.user_id = uk.user_id
    JOIN outline_keys ok ON ok.key_id = uk.key_id
    JOIN servers s ON s.server_id = ok.server_id
    WHERE DATEDIFF(uk.stop_date, NOW()) = %s;
"""

# запрос для уже истекших ключей
sql_get_expired_keys_2 = """
    SELECT u.telegram_id, uk.key_id, ok.key_value, ok.outline_key_id, s.country
    FROM user_keys uk     JOIN users u ON u.user_id = uk.user_id
    JOIN outline_keys ok ON ok.key_id = uk.key_id
    JOIN servers s ON s.server_id = ok.server_id
    WHERE stop_date < NOW();
"""

# sql_get_expired_keys_2 = """
#     SELECT u.telegram_id, uk.stop_date, ok.outline_key_id, s.country
#     FROM user_keys uk     JOIN users u ON u.user_id = uk.user_id
#     JOIN outline_keys ok ON ok.key_id = uk.key_id
#     JOIN servers s ON s.server_id = ok.server_id
#     WHERE stop_date < NOW();
# """

# # шаблоны для отправки сообщений
# message_templates = {
#     'KEY_EXPIRED': "Срок вашего ключа '<b>{name}</b>', страна '<i>{country}</i>' истек, и он был удален",
#     'KEY_EXPIRES_IN_X_DAYS': "У вас осталось {days} до конца действия ключа '<b>{name}</b>', "
#                              "страна '<i>{country}</i>'. Продлите "
#                              "действие вашего ключа, "
#                              "чтобы избежать его удаления",
#     'KEY_EXPIRES_IN_1_DAYS': "У вас остался {days} до конца действия ключа '<b>{name}</b>', "
#                              "страна '<i>{country}</i>'. Продлите "
#                              "действие вашего ключа, "
#                              "чтобы избежать его удаления",
# }

# шаблоны для отправки сообщений
message_templates = {
    'KEY_EXPIRED': "😔 Ключ закончился!\n\n"
                   "- <b>Ключ № {name}</b>\n"
                   "📍Локация '<i>{country}</i>'\n\n"
                   "✅ Купите новый ключ, если хотите продолжать пользоваться",
    'KEY_EXPIRES_IN_X_DAYS': "⏳ Осталось {days} до конца действия ключа:\n\n"
                             "- <b>Ключ № {name}</b>\n"
                             "📍Локация '<i>{country}</i>'\n\n"
                             "✅ Продлите действие вашего ключа, "
                             "чтобы избежать его удаления\n"
                             ,
    'KEY_EXPIRES_IN_1_DAYS': "⏳ Остался {days} до конца действия ключа:\n\n"
                             "- <b>Ключ № {name}</b>\n"
                             "📍Локация '<i>{country}</i>'\n\n"
                             "✅ Продлите действие вашего ключа,"
                             "чтобы избежать его удаления\n\n"
}


# корректируем дни, дней, день
def plural_days(days):
    if 10 < days % 100 < 20:
        return f"{days} дней"
    else:
        rem = days % 10
        if rem == 1:
            return f"{days} день"
        elif 2 <= rem <= 4:
            return f"{days} дня"
        else:
            return f"{days} дней"


def get_expired_keys_info():
    logger.info(f"PROCESS:get_expired_keys_info START")
    # айди по которым будем удалять из outline manager
    id_for_delete_in_manager = []
    # айди по которым будем удалять из базы данных
    id_for_delet_in_bd = []

    for days in [3, 1, 0]:

        if days == 0:
            expired_keys = execute_query(sql_get_expired_keys_2)
            logger.info(f"EXPIRED_KEYS - 0 day {expired_keys}")
        else:
            expired_keys = execute_query(sql_get_expired_keys, (days,))
            logger.info(f"EXPIRING_KEYS - {days} -  day : {expired_keys}")
        try:
            for key in expired_keys:
                # распределяем данные по переменным
                # telegram_id
                telegram_id = key[0]
                key_id = key[1]
                # name = key[2]
                outline_key_id = key[3]
                country = key[4]

                key_buttons = generate_prolong_button(key_id)

                # формируем текст собщения
                if days == 0:
                    text = message_templates['KEY_EXPIRED'].format(name=key_id,
                                                                   country=country)
                    # отправляем просроченные на удаления
                    if outline_key_id:
                        id_for_delete_in_manager.append(outline_key_id)
                    if key_id:
                        id_for_delet_in_bd.append(key_id)
                        # сообщаем об удалении
                        try:
                            sync_send_photo(telegram_id, file_ids['key_delete'], text, "HTML", main_menu_telebot())
                            logger.info(
                                f"Пользователю {telegram_id} отправлено сообщение об удалении ключа {key_id}")
                        except:
                            logger.error(f"Пользователю {telegram_id}, сообщение не доставлено, добавил в чс")


                elif days == 1:
                    # формируем текст собщения
                    text = message_templates['KEY_EXPIRES_IN_1_DAYS'].format(name=key_id,
                                                                             days=plural_days(days),
                                                                             country=country)
                    # предупреждение за 1 день и предложение продлить ключ
                    try:
                        sync_send_photo(telegram_id, file_ids['renewal'], text, "HTML", key_buttons)
                        logger.info(
                            f"Пользователю {telegram_id} отправлено сообщение об продлении ключа 1 день {key_id}")
                    except Exception as e:
                        logger.error(f"Пользователю {telegram_id}, сообщение не доставлено, добавил в чс - {e}")
                    logger.info(f"PROCESS SUCSSESS:get_expired_keys_info {id_for_delet_in_bd} - user_keys и "
                                f"{id_for_delete_in_manager} - outline_keys")

                else:

                    text = message_templates['KEY_EXPIRES_IN_X_DAYS'].format(name=key_id,
                                                                             days=plural_days(days),
                                                                             country=country)

                    # предупреждение и предложение продлить ключ
                    try:
                        sync_send_photo(telegram_id, file_ids['renewal'], text, "HTML", key_buttons)
                        logger.info(
                            f"Пользователю {telegram_id} отправлено сообщение об истечении срока действия ключа {key_id}")
                    except:
                        logger.error(f"Пользователю {telegram_id}, сообщение не доставлено, добавил в чс")
                    logger.info(f'Отправлено уведомление о продлении ключа пользователю - {telegram_id}')

                    logger.info(f"PROCESS SUCSSESS:get_expired_keys_info {id_for_delet_in_bd} - user_keys и "
                                f"{id_for_delete_in_manager} - outline_keys")

        except Exception as e:
            error = f"Ошибка при удалении ключей из баз данных ключей {id_for_delet_in_bd} " \
                    f"- user_keys и {id_for_delete_in_manager} - outline_keys, ошибка - {e}"
            logger.error(error)
            sync_send_message(err_send, error)

    # передаем ключи для удаления
    if id_for_delet_in_bd and id_for_delete_in_manager:

        if delete_from_manager(id_for_delet_in_bd, id_for_delete_in_manager):
            delete_keys(id_for_delet_in_bd)
        else:
            logger.error(f"Ошибка при удалении ключей в manager(def delete_from_manager) ключи :"
                         f" {id_for_delet_in_bd} - user_keys и "
                         f" {id_for_delete_in_manager} - outline_keys")
            txt = f"Ошибка при удалении ключей в manager(def delete_from_manager) ключи : {id_for_delet_in_bd} - " \
                  f"user_keys и {id_for_delete_in_manager} - outline_keys"
            sync_send_message(err_send, txt)


if __name__ == '__main__':
    sleep(10)
    while True:
        get_expired_keys_info()
        sleep(86400)
