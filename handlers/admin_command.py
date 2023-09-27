from config import dp, admin_from_config, bot
from aiogram import types

from keyboards.keyboards import main_menu
from logic_keys.add_keys import keys_to_send

from logger import logger

from user_data import UserData, get_list_admins_telegram_id, execute_query, QueryExecutionError

sql_add_balance = "INSERT INTO user_balance_ops (user_id, optype, amount)  VALUES (%s, 'addmoney', %s)"
sql_add_admin = "UPDATE users SET admin = %s WHERE user_id = %s"


@dp.message_handler(commands=['user_info'], state="*")
async def user_info_command(message: types.Message):
    user_data = UserData()
    admins = get_list_admins_telegram_id()

    user_id = message.get_args()

    if message.from_user.id not in (admins + admin_from_config):
        await message.reply("Данная команда только для администраторов")
        return

    try:
        keys = user_data.get_user_keys(user_id)
        answer = keys_to_send(*keys)
        info = user_data.get_user_info(user_id)

        await message.answer(info, parse_mode='HTML', disable_web_page_preview=True)

        if type(answer) == str:
            await message.answer(answer, parse_mode='HTML', disable_web_page_preview=True)
        # если список, то отправляем их по отдельности
        else:
            for country in answer:
                await message.answer(country, parse_mode='HTML', disable_web_page_preview=True)

        logger.info("ADMIN_COMMAND - /user_info")
    except Exception as e:
        logger.error(f"ERROR:ADMIN COMMANDS /user_info - Произошла ошибка при команде /user ошибка - {e}")
        await message.reply(f"Произошла ошибка: {e}")


@dp.message_handler(commands=['balance'], state="*")
async def balance_command(message: types.Message):
    keyboards = main_menu()
    command_parts = message.get_args().split()  # Разбиваем аргументы на части
    admins = get_list_admins_telegram_id()

    telegram_id = message.from_user.id

    if message.from_user.id not in (admins + admin_from_config):
        await message.reply(f"Данная команда только для администраторов")
        logger.info(f"ADMIN COMMAND - /balance, User - {telegram_id}, НЕТ ПРАВ ДЛЯ ДАННОЙ КОМАНДЫ")

    elif len(command_parts) != 2:
        await message.reply("Неверное количество аргументов, пример - /balance 142 1 или /balance 142 0")
        logger.info(f"ADMIN COMMAND - /balance, User - {telegram_id}, Неверное количество аргументов")

    else:
        user_id = command_parts[0]
        amount = command_parts[1]
        try:
            execute_query(sql_add_balance, (user_id, amount,))

            await message.reply(f"Для пользователя {user_id} пополнен баланс на {amount}.", reply_markup=keyboards)
            logger.info(f"ADMIN COMMAND - /balance, User - {telegram_id}, Для пользователя {user_id} пополнен баланс на {amount}")
        except QueryExecutionError as e:
            logger.error(f"Ошибка при выполнении команды /balance user {telegram_id},ошибка {e}")
            await message.reply(
                f"Произошла ошибка при выполнении команды /balance. Пожалуйста, обратитесь к администратору.",
                reply_markup=keyboards)


@dp.message_handler(commands=['admin'], state="*")
async def add_del_admin_command(message: types.Message):
    keyboard = main_menu()
    command_parts = message.get_args().split()  # Разбиваем аргументы на части

    admins = get_list_admins_telegram_id()

    telegram_id = message.from_user.id

    logger.info(f"ADMIN COMMAND - /admin, ADMIN - {telegram_id} ")

    if message.from_user.id not in (admins + admin_from_config):
        await message.reply(f"Данная команда только для администраторов", reply_markup=keyboard)
        logger.info(f"ADMIN COMMAND - /admin, User - {telegram_id}, НЕТ ПРАВ ДЛЯ ДАННОЙ КОМАНДЫ")

    elif len(command_parts) != 2:
        await message.reply("Неверное количество аргументов, пример - /admin 142 1 или /admin 142 0")
        logger.info(f"ADMIN COMMAND - /admin, User - {telegram_id},  , Неверное количество аргументов")
    else:
        user_id = command_parts[0]
        digit = command_parts[1]

        action = ''
        try:
            execute_query(sql_add_admin, (digit, user_id,))
            if int(digit) == 1:
                action = "Добавлен новый администратор"
            elif int(digit) == 0:
                action = "Разжалован администратор"
            logger.info(f"ADMIN COMMAND - /admin, ADMIN - {telegram_id},  {action} - {user_id}")

            await message.reply(f"{action} - {user_id}")
        except QueryExecutionError as e:
            logger.error(f"Ошибка при выполнении команды /admin: {e},  ,")
            await message.reply(f"Произошла ошибка при выполнении команды /admin,  ,")


@dp.message_handler(commands=['free'], state="*")
async def check_free_keys(message: types.Message):
    admins = get_list_admins_telegram_id()
    telegram_id = message.from_user.id
    if message.from_user.id not in (admins + admin_from_config):
        await message.reply(f"Данная команда только для администраторов")
        logger.info(f"ADMIN COMMAND - /free, User - {telegram_id}, , НЕТ ПРАВ ДЛЯ ДАННОЙ КОМАНДЫ")
        return

    User_Data = UserData()
     
    answer = User_Data.count_free_keys()

    await message.reply(answer)
    logger.info(f"ADMIN_COMMANDS /free,  , admin - {message.from_user.id}")


@dp.message_handler(commands=['all_users'], state="*")
async def check_free_keys(message: types.Message):
    User_Data = UserData()
     
    answer = User_Data.all_users()

    await message.reply(answer)
    logger.info(f"ADMIN_COMMANDS /all_users,  , admin - {message.from_user.id}")


@dp.message_handler(commands=['get_logs'], state="*")
async def check_free_keys(message: types.Message):
     
    admins = get_list_admins_telegram_id()
    telegram_id = message.from_user.id
    if message.from_user.id not in (admins + admin_from_config):
        await message.reply(f"Данная команда только для администраторов")
        logger.info(f"ADMIN COMMAND - /free, User - {telegram_id} ,НЕТ ПРАВ ДЛЯ ДАННОЙ КОМАНДЫ")
        return
    await message.reply('Загружаем логи')
    path_bot_logs = "/root/outline/bot.log"
    path_create_keys_log = "/root/create_keys/create_keys.log"

    with open(path_bot_logs, 'rb') as document:
        await bot.send_document(message.from_user.id, document)
        logger.info(f"ADMIN_COMMANDS /get_log(bot.log),  , admin - {message.from_user.id}")

    with open(path_create_keys_log, 'rb') as document:
        await bot.send_document(message.from_user.id, document)
        logger.info(f"ADMIN_COMMANDS /get_log(create_keys.log),  , admin - {message.from_user.id}")


@dp.message_handler(commands=['admin_commands'], state="*")
async def check_free_keys(message: types.Message):
     
    admins = get_list_admins_telegram_id()
    telegram_id = message.from_user.id
    if message.from_user.id not in (admins + admin_from_config):
        await message.reply(f"Данная команда только для администраторов")
        logger.info(f"ADMIN COMMAND - /free, User - {telegram_id} ,НЕТ ПРАВ ДЛЯ ДАННОЙ КОМАНДЫ")
        return
    answer = f"/get_logs - получить все логи\n\n" \
             f"/user_info - информация о пользователе 1 аргумент user_id\n\n" \
             f"/all_users - количество всех пользователей\n\n" \
             f"/free - количество свободных ключей на сервере\n\n" \
             f"/admin - назначит/разжаловать админа 2 аргумента (/admin 17 0) 17 - user_id, 1 - назначить 0 - " \
             f"разжаловать\n\n" \
             f"/balance - пополнить/уменьшить баланс пример (/balance 17 1000 или /balance 17 -1000)\n\n"

    await message.reply(answer)


# @dp.message_handler(commands=['new_prices'], state="*")
# async def balance_command(message: types.Message):
#     user_data = UserData()
#     command_parts = message.get_args().split()  # Разбиваем аргументы на части
#
#     admins = user_data.get_list_admins_telegram_id()
#
#     telegram_id = message.from_user.id
#
#     logging.info(f"ADMIN COMMAND - /admin, ADMIN - {telegram_id} ")
#
#     if telegram_id in admins:
#
#         if len(command_parts) == 2:
#             user_id = command_parts[0]
#             digit = command_parts[1]
#
#             action = ''
#
#             if int(digit) == 1:
#                 action = "Добавлен новый администратор"
#             elif int(digit) == 0:
#                 action = "Разжалован администратор"
#
#             add_del_admin(user_id, digit)
#             logging.info(f"ADMIN COMMAND - /admin, ADMIN - {telegram_id},  {action} - {user_id}")
#
#             await message.reply(f"{action} - {user_id}", parse_mode="Markdown")
#
#     else:
#         await message.reply(f"Данная команда только для администраторов", parse_mode="Markdown")
