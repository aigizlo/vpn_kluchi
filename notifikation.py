from flask import Flask, request, jsonify, abort
import hmac

from balance import add_referral_bonus
from telebot_ import main_menu_telebot, later_key_send

from config import admin, file_ids, err_send, support
from logic_keys.add_keys import add_keys
from logic_keys.renewal_keys import renewal_keys
from text import answer_if_buy
import json

from user_data import UserData, execute_query

from telebot_ import sync_send_message, sync_send_photo

import hashlib

from config import secret_key
from get_conn import create_connection
from logger import logger

app = Flask(__name__)

user_data = UserData()


# ищем user_id и сумму по pay_id, для начисления баланса данному пользователю
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
    try:
        logger.info(f'searche_key_id_user_id {pay_id}')
        sql = """SELECT key_id, user_id FROM bills WHERE pay_id  = %s"""

        result = execute_query(sql, (pay_id,))
        return result[0]
    except Exception as e:
        logger.error(f'ERROR: searche_key_id_user_id {pay_id}, {e}')


# производим покупку (если пришла оплата без key_id)
def buy_key(user_id, amount):
    from handlers.handlers import amount_to_days

    amount_float = float(amount)
    days = amount_to_days.get(int(amount_float) if amount_float.is_integer() else amount_float)

    try:

        logger.info(f"am - {amount},d -  {days}")

        _, key_value, server_id = add_keys(user_id, days)

        answer = answer_if_buy(server_id)

        key_value_message = f'<code>{key_value}</code>'

        user_info = user_data.get_user_data2(user_id)

        telegram_id = user_info.get("telegram_id")

        sync_send_photo(telegram_id, file_ids['key'], answer, "HTML")

        sync_send_message(telegram_id, key_value_message, "HTML", later_key_send())

    except Exception as e:
        logger.error(f"ERROR:Ошибка при отправке купленного ключа user_id - {user_id}, ошибка - {e} ")
        sync_send_message(err_send, f"Ошибка при отправке купленного ключа user_id - {user_id}")
        sync_send_message(telegram_id, f"Произошла ошибка, обратитесь к администратору - {support}")


# производим покупку (если пришла оплата без key_id)
def buy_key2(user_id, product):
    from config import get_mohth_with_products

    days = get_mohth_with_products.get(product) * 31

    try:

        # logger.info(f"am - {amount},d -  {days}")

        _, key_value, server_id = add_keys(user_id, days)

        answer = answer_if_buy(server_id)

        key_value_message = f'<code>{key_value}</code>'

        user_info = user_data.get_user_data2(user_id)

        telegram_id = user_info.get("telegram_id")

        sync_send_photo(telegram_id, file_ids['key'], answer, "HTML")

        sync_send_message(telegram_id, key_value_message, "HTML", later_key_send())

    except Exception as e:
        logger.error(f"ERROR:Ошибка при отправке купленного ключа user_id - {user_id}, ошибка - {e} ")
        sync_send_message(err_send, f"Ошибка при отправке купленного ключа user_id - {user_id}")
        sync_send_message(telegram_id, f"Произошла ошибка, обратитесь к администратору - {support}")


def verify_webhook(concatenated_string, token):
    hash_object = hashlib.sha256((concatenated_string).encode())
    calculated_hash = hash_object.hexdigest()

    logger.info(f'{calculated_hash} - hash, {token} - token')

    return calculated_hash == token


def is_paid(pay_id):
    try:
        logger.info(f'is_paid check {pay_id}')
        sql = """SELECT is_payed FROM bills WHERE pay_id  = %s"""

        result = execute_query(sql, (pay_id,))
        logger.info(f'{result[0]}')
        return result[0][0]
    except Exception as e:
        logger.error(f'ERROR: searche_key_id_user_id {pay_id}, {e}')
        return False


@app.route('/soft_pay_corbots', methods=['POST'])
def notify_payment_soft_pay():
    from config import secret_key_webhook

    # Получаем данные и токен из запроса
    data = request.get_data(as_text=True)
    data_dict = json.loads(data)

    amount = data_dict['amount']
    paidAmount = data_dict['paidAmount']
    paidAt = data_dict['paidAt']
    payer = data_dict['payer']
    payerEmail = data_dict['payerEmail']
    payerPhone = data_dict['payerPhone']
    productLink = data_dict["productLink"]
    promocodeName = data_dict['promocodeName']
    promocodeType = data_dict['promocodeType']
    recurrent = data_dict['recurrent']

    secret = secret_key_webhook
    status = data_dict['status']
    types = data_dict['type']

    concatenated_string = (
            str(amount) +
            str(paidAmount) +
            str(paidAt) +
            str(payer) +
            str(payerEmail) +
            str(payerPhone) +
            str(productLink) +
            str(promocodeName) +
            str(promocodeType) +
            str(recurrent).lower() +
            str(secret) +
            str(status) +
            str(types)
    )

    logger.info(concatenated_string)

    pay_id = data_dict['data']['pay_id']

    token = data_dict['token']

    logger.info(data)

    logger.info(f'Поступил платеж {amount} pay_id - {pay_id} status - {status}', )

    # Проверяем подлинность вебхука
    if not verify_webhook(concatenated_string, token):
        error_message = {'error': 'Invalid token'}
        logger.info(f"Error: {error_message}")
        return jsonify(error_message), 401

    key_id, user_id = searche_key_id_user_id(pay_id)

    logger.info(f'{key_id}, {user_id} - key user')

    try:

        if status != "CONFIRMED":
            return 401

        if is_paid(pay_id) == 1:
            logger.info(f'счет - {pay_id} уже оплачен')
            return 200

        update_pay_id_status(pay_id, 1)

        user_info = user_data.get_user_data2(user_id)

        referer_telegram = user_info.get("referer_telegram_id")

        telegram_id = user_info.get("telegram_id")

        if referer_telegram:
            ref_bonus = add_referral_bonus(user_id, amount)

            sync_send_message(referer_telegram,
                              f'Начислен реферальный бонус {ref_bonus} рублей на ваш партнерский счет!')

        if not key_id:
            buy_key2(user_id, productLink)
        else:
            key_id = renewal_keys(int(key_id), productLink)
            if key_id:
                answer = f"✅ Вы успешно продлили \"<b>Ключ № {key_id}</b>\" "

                sync_send_photo(telegram_id, file_ids['renewal_ok'], answer, "HTML", main_menu_telebot())

        logger.info(f"Webhook received and verified: {data}")

    except Exception as e:
        logger.error(f"Ошибка платежа - {e}")

    # Возвращаем успешный ответ
    return 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
