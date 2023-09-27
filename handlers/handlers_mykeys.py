from aiogram.dispatcher import FSMContext
import hashlib
from logs.logger import logger
from text import instruction

from config import dp, bot, err_send, merchant_id, project_id, secret_key
from balance.balance import pay_from_personal_balance, add_referral_bonus
from keyboards.keyboards import *
from logic_keys.add_keys import add_keys, keys_to_send
from logic_keys.renewal_keys import renewal_keys
from text import answer_if_buy, answer_if_not_balance, answer_error
from states import MyStates
from user_data import UserData, check_user_in_system
from balance.balance import money_back

amount_to_month = {
    1: 149,
    2: 269,
    3: 405,
    6: 810
}

amount_to_days = {
    149: 31,
    269: 62,
    405: 93,
    810: 186
}

server_id_country = {
    1: 'Нидерланды Амстердам',
    2: 'Германия Франкфурт',
    3: 'Казахстан Астана',
    4: 'Россия',
    5: 'Турция Стамбул'
}

user_data = UserData()


# мои ключи
@dp.message_handler(lambda message: message.text == '🔑Мои ключи', state='*')
async def my_keys_command(message: types.Message, state: FSMContext):
    if not check_user_in_system(message.from_user.id):
        await message.answer("Что бы начать работу с ботом используйте команду /start")
        return
    telegram_id = message.from_user.id
    await state.set_state(MyStates.state_my_keys)
    # current_state = await state.get_state()

    # ищем юзер_айди пользователя
    try:
        user_id = user_data.get_user_id(telegram_id)
        # получаем список имен ключей
        name_key = user_data.get_user_name_keys(user_id)
        # создаем 2 клавиатуры 1 c кнопкой "Назад" и 'Продлить ключи' если ключи есть у пользователя 2ую - если ключи есть
        keyboard = back_and_prolong_button()

        keyboard_not_keys = back_and_buy_button()

        # список всех ключей с названием и датой работы
        try:
            keys = user_data.get_user_keys(user_id)
            answer = keys_to_send(*keys)
            logger.info(f"PROCESS:my_keys_command user - {telegram_id}")

            # # ловим следующее состояние
            # await state.set_state(MyStates.state_my_keys)

            # выбор клавиатуры в зависимости от условия
            reply_keyboard = keyboard_not_keys if name_key == [] else keyboard

            # если str, значит ответ "у вас нет ключей"
            if type(answer) == str:
                await message.answer(answer, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=reply_keyboard)
            # если список, то отправляем их по отдельности
            else:
                for country in answer:
                    await message.answer(country, parse_mode='HTML', disable_web_page_preview=True,
                                         reply_markup=reply_keyboard)

                await message.answer(instruction, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=reply_keyboard)
        except Exception as e:
            logger.error(f"{e}")
    except Exception as e:
        logger.error(f"ERROR:my_keys_command, user - {telegram_id}, ошибка - {e}")
        await message.answer(answer_error, reply_markup=main_menu())


# Продлить ключи                                                              здесь ловим состояние
@dp.message_handler(lambda message: message.text == '⌛️Продлить ключи', state="*")
async def prolong_key_command(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    # ищем юзер_айди пользователя
    try:
        user_id = user_data.get_user_id(telegram_id)
        # получаем список имен ключей
        name_key = user_data.get_user_name_keys(user_id)

        if not user_data.get_user_name_keys(user_id):
            answer = "У вас нет ключей для их продления, нажмите «Назад»"
            await message.answer(answer)
            keyboard = back_button()
            await message.answer(answer, reply_markup=keyboard)
            return
        # если есть ключи, то генерируем кнопки с их названиями
        key_buttons = generate_key_buttons(name_key)
        answer = "Выберите ключ, который хотите продлить :"
        logger.info(f"PROCESS:prolong_key_command user - {telegram_id}")

        # Первое сообщение с инлайн-клавиатурой
        await message.answer(answer, reply_markup=key_buttons)

    except Exception as e:
        logger.error(f"ERROR:prolong_key_command, user - {telegram_id} ошибка - {e}")
        await message.answer(answer_error, reply_markup=main_menu())


# Выюираем какой ключ будет продлен
@dp.callback_query_handler(lambda c: c.data.startswith("select_key"), state='*')
async def process_select_key(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    try:
        # выбранный ключ для продления
        selected_key = callback_query.data.split(":")[1]
        # сохраняем этот ключ в память состояния
        await state.update_data(key_name=selected_key)
        # текущее состояние
        logger.info(f"PROCESS:process_select_key, user - {telegram_id}")

        # удаляем инлайн клавиатуру по выбору ключей
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

        # выводим клавиатуру, где юзер выбираем период продления
        keyboard = choice_renewal_period()

        await bot.send_message(callback_query.from_user.id,
                               f"Выберите период, на который хотите продлить ваш ключ: <b>{selected_key}</b>",
                               parse_mode='HTML',
                               reply_markup=keyboard)
        # передаем данные в новое состояние
        await state.set_state(MyStates.state_key_for_renewal)

        await bot.answer_callback_query(callback_query.id)

    except Exception as e:
        logger.error(f"ERROR:process_select_key, user - {telegram_id}, ошибка {e}")
        await bot.send_message(answer_error, reply_markup=main_menu())


@dp.callback_query_handler(lambda c: c.data.startswith('renewal:'), state=MyStates.state_key_for_renewal)
async def renewal_process(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        # Получаем данные из callback_data, месяц
        month = int(callback_query.data.split(':')[1])

        # формируем сумму от количества месяцев
        amount = amount_to_month.get(month, None)

        telegram_id = callback_query.from_user.id

        user_id = user_data.get_user_id(telegram_id)

        # обновляем данные состояния, и обозначаем, что это продление
        await state.update_data(user_id=user_id, action='renewal', month=month)

        # удаляем клавиатуру с выбором тарифа для продления
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)

        answer = f"Сумма покупки <b>{amount}</b> рублей, выберите способ оплаты:"

        # клава
        keyboard = get_pay_method_keyboard()

        await state.set_state(MyStates.pay_from_balance)

        logger.info(f"PROCESS:renewal, user - {telegram_id}")

        await bot.send_message(chat_id=callback_query.message.chat.id, text=answer, parse_mode='HTML',
                               reply_markup=keyboard)
    except Exception as e:
        logger.error(f"ERROR:renewal, user - {telegram_id}, ошибка - {e}")
        await bot.send_message(answer_error, reply_markup=main_menu())


methods = ['qiwi',
           'ym',
           'card',
           'advcash',
           'pm',
           'applepay',
           'googlepay',
           'samsungpay',
           'sbp',
           'payeer',
           'btc',
           'eth',
           'bch',
           'ltc',
           'dash',
           'zec',
           'doge',
           'usdt',
           'mts',
           'beeline',
           'megafon']


# обрабатываем клавиатуру get_pay_method_keyboard
@dp.callback_query_handler(lambda c: c.data.startswith("balance_pay_sever"), state=MyStates.pay_from_balance)
async def payment_from_balance(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    # берем переменные от этого состояния
    user_data_state = await state.get_data()  # Изменено с get_state() на get_data()
    # выясняем, покупка это или продление
    action = user_data_state["action"]

    User_Data = UserData()
    user_id = User_Data.get_user_id(telegram_id)
    current_balance = User_Data.get_user_balance_ops_by_user_id(user_id)
    keyboard = main_menu()
    try:

        # это класс
        User_Data = UserData()
        user_id = User_Data.get_user_id(telegram_id)
        # определяем, что это покупка
        if action == 'pay':
            # сумма
            amount = int(user_data_state["amount"])

            # проверяем если средства для оплаты
            if amount > current_balance:
                answer = answer_if_not_balance
                logger.info(f"NONE_BALANCE - нехватка средства user_id - {user_id}, cумма покупки {amount}")
                await bot.send_message(chat_id=telegram_id, text=answer, reply_markup=keyboard)
                return

            result_pay = pay_from_personal_balance(user_id, amount)
            # проводим покупку

            if not result_pay:
                answer = answer_error
                logger.info(f"PAYMENT ERROR - ошибка при оплате у user_id - {user_id}, cумма покупки {amount}")
                await bot.send_message(chat_id=telegram_id, text=answer, reply_markup=keyboard)
                return

            # определяем дни от суммы покупки
            days = amount_to_days.get(amount, None)
            # узнаем сервак
            server_id = user_data_state["server"]

            key_name = user_data_state["key_name"]
            # add_keys возвращает key_id
            key_id = await add_keys(server_id, user_id, key_name, days)
            logger.info(
                f"PROCESS:payment_from_balance, user - {user_id}, server - {server_id},summa - {amount}")
            # если key_id не вернулся
            if not key_id:
                answer = answer_error
                # возвращаем средства
                if not money_back(user_id, amount):
                    logger.error(
                        f"MONEY BACK - ERROR - средства НЕВОЗВРАЩЕНЫ на баланс user_id - {user_id}, cумма {amount}")
                logger.info(
                    f"MONEY BACK - SUCSSESS - возвращены средства на баланс user_id - {user_id}, cумма {amount}")

                await bot.send_message(err_send,
                                       f"MONEY BACK - ERROR - средства НЕВОЗВРАЩЕНЫ на баланс user_id - {user_id}, "
                                       f"cумма {amount}")
                await bot.send_message(chat_id=telegram_id,
                                       text=answer,
                                       reply_markup=keyboard)
                return

            # достаем сам ключ для отправки
            key_value = User_Data.get_key_value(key_id)
            # при успешном списании и получении ключа начисляем реферальный бонус
            referer_user_id = User_Data.get_referrer_user_id(user_id)
            if User_Data.get_referrer_user_id(user_id):
                referer_telegram = User_Data.get_tg_if_use_user_id(referer_user_id)
                if not add_referral_bonus(user_id, amount):
                    await bot.send_message(chat_id=err_send,
                                           text=f"Не удалось начислить реферальный бонус пользователю {user_id}")
                await bot.send_message(referer_telegram, f'Вам начислен реферальный бонус {amount * 0.2} рублей')
            # если покупка прошла успешно, ты высылаем ему ключ
            answer = answer_if_buy(key_value)

            # удаляем предыдущее сообщение
            await bot.delete_message(chat_id=telegram_id,
                                     message_id=callback_query.message.message_id)

            await bot.send_message(chat_id=telegram_id,
                                   text=answer,
                                   parse_mode="HTML",
                                   disable_web_page_preview=True,
                                   reply_markup=keyboard)

            await state.finish()  # или await state.set_state("another_state")

        # если это продление, а не покупка
        if action == "renewal":
            # период на которое продлевается ключ
            month = user_data_state["month"]
            # имя ключа
            key_name = user_data_state["key_name"]
            # сумма покупки
            amount = amount_to_month.get(month, None)
            logger.info(
                f"PROCESS:payment_from_balance - RENEWAL, user - {user_id}, key_name -  {key_name},summ -  {amount}")

            if amount > current_balance:
                answer = answer_if_not_balance
                logger.info(
                    f"NONE_BALANCE - нехватка средств при продлении user_id - {user_id}, cумма покупки {amount}")
                await bot.send_message(chat_id=telegram_id, text=answer, reply_markup=keyboard)
                return

            if not pay_from_personal_balance(user_id, amount):
                answer = answer_error
                logger.info(f"PAYMENT ERROR - ошибка при продлении ключа у user_id - {user_id}, cумма покупки {amount}")
                await bot.send_message(chat_id=telegram_id, text=answer, reply_markup=keyboard)
                return

            if not renewal_keys(user_id, key_name, month):
                await bot.send_message(chat_id=telegram_id, text=answer_error, reply_markup=keyboard)
                if not money_back(user_id, amount):
                    await bot.send_message(err_send, f"Ошибка возврата средств на баланс {user_id},cумма {amount}")
                return

            if User_Data.get_referrer_user_id(user_id):
                if not add_referral_bonus(user_id, amount):
                    await bot.send_message(chat_id=err_send,
                                           text=f"Не удалось начислить реферальный бонус пользователю {user_id}")

            answer = f"Продления ключа \"<b>{key_name}</b>\" прошло успешно👌!\nСпасибо, что выбрали <b>OutlineX!</b> 😇"
            keyboard = main_menu()
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
            await bot.send_message(chat_id=callback_query.message.chat.id, text=answer, parse_mode="HTML",
                                   reply_markup=keyboard)

            await state.finish()  # или await state.set_state("another_state")

    except Exception as e:
        logger.error(f"ERROR:payment_from_balance, user {telegram_id}, ошибка - {e}")
        await bot.send_message(telegram_id, answer_error, reply_markup=main_menu())
        await bot.send_message(err_send, f"ERROR:payment_from_balance, user {telegram_id} , ошибка - {e}")
