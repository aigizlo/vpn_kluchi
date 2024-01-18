from flask import Flask, request
from telebot_ import main_menu_telebot

from config import admin
from logic_keys.add_keys import add_keys
from logic_keys.renewal_keys import renewal_keys
from text import answer_if_buy

from user_data import UserData, execute_query

from telebot_ import sync_send_message, sync_send_photo

import hashlib

from config import secret_key
from get_conn import create_connection
from logger import logger

app = Flask(__name__)

user_data = UserData()


# ищем user_id и сумму по pay_id, для начисление баланса данному пользователю
def get_user_id_and_amount_from_bills(pay_id):
    sql_user_id_amount = "SELECT user_id, amount FROM bills WHERE pay_id = %s"
    try:
        with create_connection() as mydb, mydb.cursor(buffered=True) as mycursor:
            mycursor.execute(sql_user_id_amount, (pay_id,))
            result = mycursor.fetchone()
            return result
    except Exception as e:
        logger.error(f"ERROR - get_user_id_from_bills, {e}")
        return False


def update_pay_id_status(pay_id, status):
    with create_connection() as mydb, mydb.cursor(buffered=True) as mycursor:
        try:

            sql_paid_data = "UPDATE bills SET is_payed = %s WHERE pay_id = %s"

            pay_id = int(pay_id)

            mycursor.execute(sql_paid_data, (status, pay_id,))

            logger.info(f"update_pay_id_status - SUCSSESS: pay_id - {pay_id}, status - {status}")

            return True
        except Exception as e:
            logger.error(f"update_pay_id_status - FAILED: pay_id - {pay_id}, status - {status}, ERROR - {e}")
            return False


# здесь определяем есть ли key_id и какой юзер
def searche_key_id_user_id(pay_id):
    sql = """SELECT key_id, user_id FROM bills WHERE pay_id  = %s"""

    result = execute_query(sql, (pay_id,))

    return result[0]


def buy_key(user_id, amount):
    from handlers.handlers import amount_to_days

    days = amount_to_days.get(int(amount))

    logger.info(f"am - {amount},d -  {days}")

    _, key_value, server_id = add_keys(user_id, days)

    answer = answer_if_buy(key_value, server_id)

    telegram_id = user_data.get_tg_if_use_user_id(user_id)

    with open('images/key.jpeg', 'rb') as photo:
        sync_send_photo(telegram_id, photo, answer, "HTML", main_menu_telebot())


# обновляем статус платежа на оплаченый
def notifi_user(user_id, key_id):
    telegram_id = user_data.get_tg_if_use_user_id(user_id)

    answer = f"Продления ключа \"<b>Ключ № {key_id}</b>\" прошло успешно👌!\nСпасибо, что выбрали <b>«Off Radar»!!</b> 😇"

    with open('images/key.jpeg', 'rb') as photo:
        sync_send_photo(telegram_id, photo, answer, "HTML", main_menu_telebot())


@app.route('/notification_corbots', methods=['POST'])
def payment_notification():
    # Получаем параметры из POST-запроса
    data = request.form.to_dict()

    # Формируем строку для подписи
    signature_data = ':'.join([
        data['currency'],
        data['amount'],
        data['pay_id'],
        data['merchant_id'],
        data['status'],
        secret_key

    ])

    # Вычисляем SHA256 подпись
    calculated_signature = hashlib.sha256(signature_data.encode()).hexdigest()

    # Проверяем подпись
    if calculated_signature != data['sign']:
        logger.info("Ошибка в подписи")
        return 'Wrong Sign!', 400
    currency = data['currency']
    amount = data['amount']
    pay_id = data['pay_id']
    merchant_id = data['merchant_id']
    status = data['status']
    logger.info(f"Поступили данные ANY PAY {currency}, {amount}, {pay_id}, {merchant_id}, {status}")
    # проверяем покупка это или продление
    key_id, user_id = searche_key_id_user_id(pay_id)
    # если key_id = None то это покупка, в остальных - продление

    # logger.info(key_id, user_id)

    if status == 'paid':
        status = 1
        update_pay_id_status(pay_id, status)

    if not key_id:
        buy_key(user_id, amount)
    else:
        key_id = renewal_keys(int(key_id), int(amount))
        if key_id:
            notifi_user(user_id, key_id)

    logger.info(f"Поступили данные ANY PAY {currency}, {amount}, {pay_id}, {merchant_id}, {status}")
    sync_send_message(admin, text=f"Поступил платеж на сумму {amount} рублей")

    return 'OK', 200

#
# @app.route('/notifi_payment_fropay_den', methods=['POST'])
# def payment_status():
#     from config import shop_id_fropay, secret_key_fropay
#     try:
#         data = request.form
#         pay = data['pay']  # Номер платежа в системе FROPAY
#         pay_id = data['label']  # ID платежа в вашей системе
#         amount = data['amount']  # Сумма платежа в формате 100.00
#         hashsign = data['hash']  # Зашифрованная строка методом sha256
#
#         # Генерируем хеш для проверки
#         sign = hashlib.sha256((shop_id_fropay + amount + secret_key_fropay + pay_id + pay).encode('utf-8')).hexdigest()
#
#         if sign != hashsign:
#             return 'Неверный hash', 400  # Ошибка при неверном хеше
#
#         key_id, user_id = searche_key_id_user_id(pay_id)
#
#         update_pay_id_status(pay_id, 1)
#
#         if not key_id:
#             buy_key(user_id, amount)
#         else:
#             key_id = renewal_keys(int(key_id), int(amount))
#             if key_id:
#                 notifi_user(user_id, key_id)
#
#         logger.info(f"Поступили данные fro_pay, {amount}, pay_id -{pay_id}, {pay}")
#         sync_send_message(admin, f"Поступил платеж на сумму {amount} рублей")
#
#         return 'OK', 200
#
#     except Exception as e:
#         return str(e), 400  # Ошибка при обработке запроса


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
