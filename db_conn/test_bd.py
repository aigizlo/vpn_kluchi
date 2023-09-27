import get_conn

mydb = get_conn.create_connection()

cursor = mydb.cursor()
from logs.logger import logger

#
#
# def get_server_id():  # ищем serve_id по key_id
#   try:
#     cursor.execute("SELECT telegram_id FROM users WHERE admin = 1")
#     result = cursor.fetchall()
#
#     return result
#
#   except Exception as e:
#     logger.error("Ошибка при поиске server_id", e)

# def count_free_keys():
#     cursor.execute("""SELECT server_id, COUNT(*) AS count
#                       FROM outline_keys
#                             WHERE used = 0 AND server_id IN (1, 2, 3, 4, 5)
#                             GROUP BY server_id;""")
#     result = cursor.fetchone()
#     return result
# count_free_keys()

# telegram_id = 502811372
#
# mycursor.execute("SELECT referer_id FROM users WHERE telegram_id = %s", (telegram_id,))
#
# result = mycursor.fetchone()
#
# print(result)


# def name_keys(telegram_id):
#   try:
#     mycursor = mydb.cursor(buffered=True)
#
#     mycursor.execute("SELECT user_id FROM users WHERE telegram_id = %s", (telegram_id,))
#     result_id = mycursor.fetchone()
#     user_id = result_id[0]
#
#     # запрос для получени ключа, имени ключа, даты окончания сервер 1
#     mycursor.execute(
#       f"SELECT uk.name FROM outline_keys ok JOIN user_keys uk ON ok.key_id = uk.key_id WHERE uk.user_id = {user_id}"
#     )
#     name_keys = mycursor.fetchall()
#
#     return name_keys
#
#   except mysql.connector.errors.ProgrammingError as err:
#     answer = "Произошла ошибка, обратитесь к администратору 1231"
#     logger.error(f'Произошла ошибка при попытке найти ключи в БД,пользователь: {user_id}, время {now} ', err)
#     return answer
# name_key = name_keys(502811372)
# print(name_keys(502811372))
#
# for name in name_key:
#   print(name[0])
# mycursor.execute(
#     "INSERT INTO users (username, telegram_id) VALUES (%s, %s)",
#     ("valera", 748728735)
# )

#
# user_id = [9]
# mycursor.execute("SELECT key_id  FROM user_keys WHERE user_id = %s", (user_id))
# key_ids = []
#
#
# for key_id in mycursor:
#   key_ids.append(key_id[0])
#
# print(key_ids)


# mycursor.execute("SELECT * FROM outline_keys WHERE used = %s", ([0]))
#
#
# result_id = mycursor.fetchone()
# _key_id, _outline_id,_sever_id, _key_value, _used = result_id
#
# print(_key_id, _outline_id, _key_value)


# # обращаемся к таблице users по telegram_id и забираем user_id
# telegram_id = [502811372]
# mycursor.execute("SELECT * FROM users WHERE telegram_id = %s", (telegram_id))
# result_id = mycursor.fetchone()
# user_id = result_id[0]
#
# mycursor.execute("SELECT key_id  FROM user_keys WHERE user_id = %s", (user_id,))
# key_ids = []
# keys = []
# for key_id in mycursor:
#   key_ids.append(key_id[0])
#
#
# for i in key_ids:
#     mycursor.execute("SELECT key_value  FROM outline_keys WHERE key_id = %s", (i,))
#     keys.append(mycursor.fetchone())
#
# print(type(keys))



# mycursor.execute(f'SELECT server_id FROM outline_keys WHERE key_id = 7421')
# result = mycursor.fetchall()
# if result:
#   print(result[0][0])
# else:
#   print("this keys is not")
# # user_id = 502811372
# # # query = f'SELECT ok.key_value, uk.stop_date  FROM outline_keys ok  JOIN user_keys uk ON ok.key_id = uk.key_id WHERE uk.user_id = 14 AND ok.server_id = 2;'
# # query = "SELECT user_id FROM users WHERE telegram_id = 502811372"
# # mycursor.execute(query)
# #
# #
# # result = mycursor.fetchall()
# # print(result)
# #
# # mydb.close()  # Закрываем подключение