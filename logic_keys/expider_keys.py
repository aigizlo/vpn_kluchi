from keyboards.keyboards import generate_prolong_button
from logger import logger

from sender import send_message, send_message_no_parse_mode, send , err_send,bot

from logic_keys.delete_keys import delete_keys, delete_from_manager

from get_conn import create_connection
from user_data import execute_query

# запрос для получения ключей которые скоро истекут
sql_get_expired_keys = """
    SELECT u.telegram_id, uk.key_id, uk.name, ok.key_value, ok.outline_key_id, s.country
    FROM user_keys uk     JOIN users u ON u.user_id = uk.user_id
    JOIN outline_keys ok ON ok.key_id = uk.key_id
    JOIN servers s ON s.server_id = ok.server_id
    WHERE DATEDIFF(uk.stop_date, NOW()) = %s;
"""

# запрос для уже истекших ключей
sql_get_expired_keys_2 = """
    SELECT u.telegram_id, uk.key_id, uk.name, ok.key_value, ok.outline_key_id, s.country
    FROM user_keys uk     JOIN users u ON u.user_id = uk.user_id
    JOIN outline_keys ok ON ok.key_id = uk.key_id
    JOIN servers s ON s.server_id = ok.server_id
    WHERE stop_date < NOW();
"""

# шаблоны для отправки сообщений
message_templates = {
    'KEY_EXPIRED': "Срок вашего ключа '<b>{name}</b>', страна '<i>{country}</i>' истек, и он был удален",
    'KEY_EXPIRES_IN_X_DAYS': "У вас осталось {days} до конца действия ключа '<b>{name}</b>', страна '<i>{country}</i>'. Продлите "
                             "действие вашего ключа, "
                             "чтобы избежать его удаления",
    'KEY_EXPIRES_IN_1_DAYS': "У вас остался {days} до конца действия ключа '<b>{name}</b>', страна '<i>{country}</i>'. Продлите "
                             "действие вашего ключа, "
                             "чтобы избежать его удаления",
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


# ищем истекающие и истекшие ключи и отправляем соответсвующее уведомление
async def get_expired_keys_info():
    logger.info(f"PROCESS:get_expired_keys_info START")
    # айди по которым будем удалять из outline manager
    id_for_delete_in_manager = []
    # айди по которым будем удалять из базы данных
    id_for_delet_in_bd = []

    for days in [5, 2, 1, 0]:

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
                id = key[0]
                key_id = key[1]
                name = key[2]
                outline_key_id = key[4]
                country = key[5]

                key_buttons = generate_prolong_button(name)

                # формируем текст собщения
                if days == 0:
                    text = message_templates['KEY_EXPIRED'].format(name=name,
                                                                   country=country)
                    # отправляем просроченные на удаления
                    if outline_key_id:
                        id_for_delete_in_manager.append(outline_key_id)
                    if key_id:
                        id_for_delet_in_bd.append(key_id)
                        # сообщаем об удалении
                        await send(id, text)

                elif days == 1:
                    # формируем текст собщения
                    text = message_templates['KEY_EXPIRES_IN_1_DAYS'].format(name=name,
                                                                             days=plural_days(days),
                                                                             country=country)
                    # предупреждение за 1 день и предложение продлить ключ
                    await send_message(id, text, key_buttons)
                    logger.info(f"PROCESS SUCSSESS:get_expired_keys_info {id_for_delet_in_bd} - user_keys и "
                                f"{id_for_delete_in_manager} - outline_keys")

                else:

                    text = message_templates['KEY_EXPIRES_IN_X_DAYS'].format(name=name,
                                                                             days=plural_days(days),
                                                                             country=country)

                    # предупреждение и предложение продлить ключ
                    await send_message(id, text, key_buttons)
                    logger.info(f"PROCESS SUCSSESS:get_expired_keys_info {id_for_delet_in_bd} - user_keys и "
                                f"{id_for_delete_in_manager} - outline_keys")

        except Exception as e:
            logger.error(f"Ошибка при удалении ключей из баз данных ключей {id_for_delet_in_bd} - user_keys и "
                         f"{id_for_delete_in_manager} - outline_keys, ошибка - {e} ")

    # передаем ключи для удаления
    if id_for_delet_in_bd and id_for_delete_in_manager:

        if await delete_from_manager(id_for_delet_in_bd, id_for_delete_in_manager):
            delete_keys(id_for_delet_in_bd)
        else:
            logger.error(f"Ошибка при удалении ключей в manager(def delete_from_manager) ключи :"
                         f" {id_for_delet_in_bd} - user_keys и "
                         f" {id_for_delete_in_manager} - outline_keys")
            await bot.send_message(err_send, f"Ошибка при удалении ключей в manager(def delete_from_manager) ключи :"
                                             f" {id_for_delet_in_bd} - user_keys и "
                                             f" {id_for_delete_in_manager} - outline_keys")
