from flask import Flask, request, jsonify

import hashlib

from config import secret_key
from get_conn import create_connection
from logger import logger

app = Flask(__name__)


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


def add_balance(pay_id, status):
    sql_add_balance = "INSERT INTO user_balance_ops (user_id, optype, amount)  VALUES (%s, 'addmoney', %s)"
    user_id_amount = get_user_id_and_amount_from_bills(pay_id)
    try:
        with create_connection() as mydb, mydb.cursor(buffered=True) as mycursor:
            if not set_bill_payed(pay_id, status):
                return False
            if not user_id_amount:
                return False
            mycursor.execute(sql_add_balance(user_id_amount))
            if mycursor.rowcount == 0:
                return False
            logger.info(f"add_balance - SUCSSESS: Начислен баланс пользователю "
                        f"{user_id_amount[0]}, {user_id_amount[1]} рублей по платежу {pay_id}")

    except Exception as e:
        logger.error(f"add_balance - FAILED: pay_id - {pay_id}, status - {status}, ERROR - {e}")
        return False


def set_bill_payed(pay_id, status):
    with create_connection() as mydb, mydb.cursor(buffered=True) as mycursor:
        try:

            sql_paid_data = "UPDATE bills SET is_payed = %s WHERE pay_id = %s"

            pay_id = int(pay_id)

            mycursor.execute(sql_paid_data, (status, pay_id,))

            logger.info(f"new_info - SUCSSESS: pay_id - {pay_id}, status - {status}")

            return True
        except Exception as e:
            logger.error(f"new_info - FAILED: pay_id - {pay_id}, status - {status}, ERROR - {e}")
            return False


# IP адреса, с которых ожидаются запросы
allowed_ips = ['185.162.128.38', '185.162.128.39', '185.162.128.88']


@app.route('/notification', methods=['POST'])
def payment_notification():
    # Получаем параметры из POST-запроса
    data = request.form.to_dict()

    # Проверяем IP адрес
    if request.remote_addr not in allowed_ips:
        logger.info("Bad IP!")
        return 'Bad IP!', 403


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

    logger.info(f"Поступили данные {currency}, {amount}, {pay_id}, {merchant_id}, {status}")

    if status == 'paid':
        status = 1

    if add_balance(pay_id, status):
        return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)