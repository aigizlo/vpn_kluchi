from config import coefficeint_bonus, partners, partner_bonus
from get_conn import create_connection
from logger import logger
import math

from user_data import UserData, execute_query

# запрос для оплаты с реф баланса
sql_pay_from_bonus_query = """INSERT INTO user_balance_ops 
            (user_id, optype, amount)
                        VALUES (%s, 'bonus', -%s)"""

#
# запрос для начисления реферального бонуса
sql_add_referral_bonus = """INSERT INTO user_balance_ops 
            (user_id, optype, amount)
                        VALUES (%s, 'bonus', %s)"""

# инициализируем класс UserData для его использования
user_data = UserData()


def add_referral_bonus(user_id, purchase_amount):
    try:
        # Преобразуем purchase_amount в число с плавающей точкой, если это возможно.
        # Если purchase_amount является строкой, которая содержит число, это будет работать.
        # Если строка не может быть преобразована в число, будет сгенерировано исключение ValueError.
        purchase_amount = float(purchase_amount)

        # ищем юзер_айди реферера
        referer_user_id = user_data.get_referrer_user_id(user_id)

        if referer_user_id in partners:
            bonus_rub = purchase_amount * partner_bonus
            bonus_rub = math.floor(bonus_rub)
        else:
            bonus_rub = purchase_amount * coefficeint_bonus
            bonus_rub = math.floor(bonus_rub)

        execute_query(sql_add_referral_bonus, (referer_user_id, bonus_rub))
        logger.info(f"REFERRAL_BONUS_SUCCESS: Начислен реферальный бонус user - "
                    f"{referer_user_id}, на сумму {bonus_rub}")
        return bonus_rub
    except ValueError:
        logger.error(f"REFERRAL_BONUS_FAILED: Ошибка, purchase_amount не является числом")
        return False
    except Exception as e:
        logger.error(f"REFERRAL_BONUS_FAILED: Ошибка при начислении реферального бонуса - {e}")
        return False


def pay_from_referral_balance(user_id, amount):
    current_balance = user_data.get_user_balance_bonus(user_id)
    try:
        execute_query(sql_pay_from_bonus_query, (user_id, amount))
        logger.info(f"PROCESS:pay_from_referral_balance : Покупка на сумму {amount} прошла успешно, "
                    f"пользователь - {user_id}")
        return True

    except Exception as e:
        logger.ERROR(f"ERROR:pay_from_referral_balance : Произошла ошибка при покупке на сумму - {amount}, "
                     f"у пользователя {user_id}, его баланс {current_balance}, "
                     f"Ошибка: {e}")
        return False


#
def money_back(user_id, money):
    sql_add_referral_bonus = """INSERT INTO user_balance_ops 
                (user_id, optype, amount)
                            VALUES (%s, 'bonus', %s)"""
    try:
        execute_query(sql_add_referral_bonus, (user_id, money,))
        logger.info(
            f"MONEY BACK - SUCSSESS - возвращены средства на баланс user_id - {user_id}, cумма {money}")
        return True
    except Exception as e:
        logger.error(
            f"MONEY BACK - ERROR - средства НЕВОЗВРАЩЕНЫ на баланс user_id - {user_id}, cумма {money}, ошибка - {e}")
        return False


# cоздаем неоплаченный платеж в базе bills для покупки (НЕ ПРОДЛЕНИЕ)
def creating_payment(amount, user_id):
    try:

        with create_connection() as mydb, mydb.cursor(buffered=True) as mycursor:

            sql_create_bill = "INSERT INTO bills (amount, user_id) VALUES (%s, %s)"

            mycursor.execute(sql_create_bill, (amount, user_id,))
            pay_id = mycursor.lastrowid

            logger.info(f"CREATE PAYMENT - SUCSSESS: user_id - {user_id}, amount - {amount}, pay_id - {pay_id}")

        return mycursor.lastrowid

    except Exception as e:
        logger.error(f"CREATE PAYMENT - FAILED: user_id - {user_id}, amount - {amount}, ERROR - {e}")


def creating_payment_for_renewal(amount, user_id, key_id):
    try:

        with create_connection() as mydb, mydb.cursor(buffered=True) as mycursor:

            sql_create_bill = "INSERT INTO bills (amount, user_id, key_id) VALUES (%s, %s, %s)"

            mycursor.execute(sql_create_bill, (amount, user_id, key_id,))

            pay_id = mycursor.lastrowid

            logger.info(f"CREATE PAYMENT - SUCSSESS: user_id - {user_id}, amount - {amount}, pay_id - {pay_id}")

        return mycursor.lastrowid

    except Exception as e:
        logger.error(f"CREATE PAYMENT - FAILED: user_id - {user_id}, amount - {amount}, ERROR - {e}")
