import aiogram
from aiogram.dispatcher import FSMContext
from create_pay_links import generate_any_pay_link, generate_free_kassa, create_order
from handlers.handlers import amount_to_days
from logger import logger
from logic_keys.renewal_keys import renewal_keys
from text import answer_not_keys, answer_if_not_balance, answer_if_buy

from config import dp, bot, secret_key, file_ids, err_send, products, products_price
from balance import creating_payment, creating_payment_for_renewal, pay_from_referral_balance, money_back
from keyboards.keyboards import *
from logic_keys.add_keys import keys_send, add_keys
from text import answer_error
from states import MyStates
from user_data import UserData, check_user_in_system

amount_to_month = {
    1: one_month,
    3: three_month,
    12: one_year
}
# для тестов
#
#
# amount_to_days = {
#     149: 0,
#     269: 1,
#     405: 2,
#     810: 3
# }

#


user_data = UserData()


# мои ключи
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('my_keys'), state='*')
async def my_keys(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id

    if not check_user_in_system(telegram_id):
        await bot.send_message(chat_id=telegram_id, text="Что бы начать работу с ботом используйте команду /start")
        return

    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")

    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    user_id = user_info[0]

    # обновляем последнее действие пользователя
    user_data.update_last_activity(user_id)

    # ищем юзер_айди пользовател
    try:
        # получаем список имен ключей
        key_ids = user_data.get_key_ids(user_id)
        # создаем 2 клавиатуры 1 c кнопкой "Назад" и 'Продлить ключи' если ключи есть у пользователя 2ую - если ключей нет
        keyboard = keyboard_if_have_keys()

        keyboard_not_keys = keyboard_if_not_keys()

        # список всех ключей с названием и датой работы
        try:
            keys = user_data.get_user_keys_info(user_id)

            answer = keys_send(keys)

            if not answer:
                answer = answer_not_keys

            logger.info(f"BUTTON:my_keys - Мои ключи user - {user_info}")

            # выбор клавиатуры в зависимости от условия
            reply_keyboard = keyboard_not_keys if key_ids == [] else keyboard

            await bot.send_photo(chat_id=telegram_id,
                                 photo=file_ids['my_keys'],
                                 caption=answer,
                                 parse_mode="HTML",
                                 reply_markup=reply_keyboard)

        except Exception as e:
            logger.error(f"ERROR - BUTTON:my_keys, user - {user_info}, ошибка - {e}")
    except Exception as e:
        logger.error(f"ERROR - BUTTON:my_keys, user - {user_info}, ошибка - {e}")


# Продлить ключи                                                              здесь ловим состояние
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('prolong_keys'), state='*')
async def prolong_key_command(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_userid_firsname_nickname(telegram_id)
    user_id = user_info[0]

    # обновляем последнее действие пользователя
    user_data.update_last_activity(user_id)

    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")
    # ищем юзер_айди пользователя
    try:
        # получаем список key id
        key_ids = user_data.get_key_ids(user_id)

        if not key_ids:
            answer = "У вас нет ключей для их продления"
            keyboard = main_menu_inline()
            await bot.send_message(text=answer, chat_id=telegram_id, reply_markup=keyboard)
            return
        # если есть ключи, то генерируем кнопки с их названиями
        key_buttons = generate_key_buttons(key_ids)
        answer = "Выберите ключ, который хотите продлить :"
        logger.info(f"BUTTON:prolong_keys - Продлить ключи user - {user_info}")

        # Первое сообщение с инлайн-клавиатурой

        await bot.send_photo(chat_id=telegram_id,
                             photo=file_ids['renewal'],
                             caption=answer,
                             reply_markup=key_buttons)

    except Exception as e:
        logger.error(f"ERROR - BUTTON:prolong_keys user - {user_info} ошибка - {e}")
        # await message.answer(answer_error, reply_markup=main_menu_inline())


# Выюираем какой ключ будет продлен
@dp.callback_query_handler(lambda c: c.data.startswith("select_key"), state='*')
async def process_select_key(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_userid_firsname_nickname(telegram_id)
    user_id = user_info[0]
    # обновляем последнее действие пользователя
    user_data.update_last_activity(user_id)

    try:
        # выбранный ключ для продления
        selected_key = callback_query.data.split(":")[1]

        # сохраняем этот ключ в память состояния
        await state.update_data(key_id=selected_key)
        # текущее состояние
        logger.info(f"RENEWAL_KEY_SELECTED - {selected_key}, user - {user_info}")

        # удаляем инлайн клавиатуру по выбору ключей
        try:
            if callback_query.message.message_id:
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.message_id)
        except aiogram.utils.exceptions.MessageCantBeDeleted:
            logger.info("Сообщение не может быть удалено.")

        # выводим клавиатуру, где юзер выбираем период продления
        keyboard = choice_renewal_period()

        answer = f"""Вы выбрали ключ № <b>{selected_key}</b>

⏳ Выберите период, на который хотите продлить ваш ключ:
"""

        await bot.send_photo(chat_id=telegram_id,
                             photo=file_ids['renewal'],
                             caption=answer,
                             parse_mode='HTML',
                             reply_markup=keyboard)

        # передаем данные в новое состояние
        await state.set_state(MyStates.state_key_for_renewal)

    except Exception as e:
        logger.error(f"ERROR:RENEWAL_KEY_SELECTED - {selected_key}, user - {user_info}, "
                     f"user - {telegram_id}, ошибка {e}")
        await bot.send_message(answer_error, reply_markup=main_menu_inline())


@dp.callback_query_handler(lambda c: c.data.startswith('renewal:'), state=MyStates.state_key_for_renewal)
async def renewal_process(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id

    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    user_id = user_info[0]

    # обновляем последнее действие пользователя
    user_data.update_last_activity(user_id)

    # берем переменные от этого состояния
    user_data_state = await state.get_data()

    key_id = user_data_state["key_id"]

    amount = int(callback_query.data.split(':')[1])

    try:
        # Получаем данные из callback_data, месяц
        price = int(callback_query.data.split(':')[1])

        # удаляем клавиатуру с выбором тарифа для продления
        try:
            if callback_query.message.message_id:
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.message_id)
        except aiogram.utils.exceptions.MessageCantBeDeleted:
            logger.info("Сообщение не может быть удалено.")
        await state.set_state(MyStates.pay_from_balance)
        logger.info(f"renewal_key {key_id}, user - {user_info} на сумму {price}")

        answer = f"Сумма покупки <b>{price}</b> рублей, выберите способ оплаты:\n" \
        # -------------------------
        pay_id = creating_payment_for_renewal(price, user_id, key_id)

        order_link = create_order(products_price.get(amount), pay_id)

        await state.update_data(user_id=user_id, action='renewal', amount=amount, pay_id=pay_id,
                                fk_link=order_link)

        await state.set_state(MyStates.pay_from_balance)

        if order_link:
            keyboard = kb_pay(price, order_link)
            await bot.send_photo(chat_id=telegram_id,
                                 photo=file_ids['bill'],
                                 caption=answer,
                                 parse_mode="HTML",
                                 reply_markup=keyboard)
            logger.info(f"BOT_SEND_PAY_LINK - {order_link}, user - {user_info}")

        else:
            await bot.send_message(telegram_id, "Ошибка при генерации ссылки для оплаты, обратитесь в службу поддержки")
            logger.info(f"ERROR - BOT_SEND_PAY_LINK, user - {user_info}")
    except Exception as e:
        logger.error(f"ERROR - renewal_key Ошибка при продлении ключа, user - {user_info}, ошибка - {e}")
        await bot.send_message(telegram_id, answer_error, reply_markup=main_menu_inline())


# обрабатываем клавиатуру get_pay_method_keyboard
@dp.callback_query_handler(lambda c: c.data.startswith("balance_ref"), state=MyStates.pay_from_balance)
async def payment_from_balance(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    # берем переменные от этого состояния
    user_data_state = await state.get_data()  # Изменено с get_state() на get_data()
    # выясняем, покупка это или продление
    action = user_data_state["action"]

    user_id = user_info[0]
    # current_balance = user_data.get_user_balance_ops_by_user_id(user_id)
    keyboard = main_menu_inline()

    fk_link = user_data_state["fk_link"]
    # any_pay_link = user_data_state["any_pay_link"]

    current_balance = user_data.get_user_balance_bonus(user_id)

    try:
        # определяем, что это покупка
        if action == 'pay':
            # сумма
            amount = int(user_data_state["amount"])
            # проверяем если средства для оплаты
            if amount > current_balance:
                answer = answer_if_not_balance

                logger.info(f"NONE_BALANCE - нехватка средства user - {user_info}, cумма покупки {amount}")
                await bot.send_message(chat_id=telegram_id, text=answer, reply_markup=online_pay(fk_link))
                return

            result_pay = pay_from_referral_balance(user_id, amount)
            # проводим покупку

            if not result_pay:
                answer = answer_error
                logger.info(f"PAYMENT ERROR - ошибка при оплате у user - {user_info}, cумма покупки {amount}")

                await bot.send_message(chat_id=telegram_id, text=answer, reply_markup=keyboard)
                return

            # определяем дни от суммы покупки
            days = amount_to_days.get(amount, None)

            key_id, key_value, server_id = add_keys(user_id, days)
            logger.info(f"{key_id} - key_id")
            logger.info(
                f"Оплата, user - {user_info}, server - {server_id},сумма - {amount}")
            # если key_id не вернулся
            if not key_id:
                answer = answer_error
                # возвращаем средства
                if not money_back(user_id, amount):
                    logger.error(
                        f"MONEY BACK - ERROR - средства НЕВОЗВРАЩЕНЫ на баланс user - {user_info}, cумма {amount}")
                logger.info(
                    f"MONEY BACK - SUCSSESS - возвращены средства на баланс uuser - {user_info}, cумма {amount}")

                await bot.send_message(err_send,
                                       f"MONEY BACK - ERROR - средства НЕВОЗВРАЩЕНЫ на баланс user - {user_info}, "
                                       f"cумма {amount}")
                await bot.send_message(chat_id=telegram_id,
                                       text=answer,
                                       reply_markup=keyboard)
                return

            # если покупка прошла успешно, ты высылаем ему ключ
            answer = answer_if_buy(server_id)

            key_send = f'<code>{key_value}</code>'

            # удаляем предыдущее сообщение
            await bot.delete_message(chat_id=telegram_id,
                                     message_id=callback_query.message.message_id)

            await bot.send_photo(chat_id=telegram_id,
                                 photo=file_ids['key'],
                                 caption=answer,
                                 parse_mode="HTML")

            await bot.send_message(chat_id=telegram_id,
                                   text=key_send,
                                   parse_mode="HTML")

            await state.finish()  # или await state.set_state("another_state")

        # если это продление, а не покупка
        if action == "renewal":
            # период на которое продлевается ключ
            amount = user_data_state["amount"]

            # имя ключа
            key_id = user_data_state["key_id"]
            # сумма покупки
            logger.info(
                f"PROCESS:Оплата продления , user - {user_info}, key_id -  {key_id}, сумма -  {amount}")

            if amount > current_balance:
                answer = answer_if_not_balance
                logger.info(
                    f"NONE_BALANCE - нехватка средств при продлении user - {user_info}, cумма покупки {amount}")
                await bot.send_message(chat_id=telegram_id, text=answer, reply_markup=online_pay(fk_link))
                return

            else:
                if not pay_from_referral_balance(user_id, amount):
                    answer = answer_error
                    logger.info(
                        f"PAYMENT ERROR - ошибка при продлении ключа у user - {user_info}, cумма покупки {amount}")
                    await bot.send_message(chat_id=telegram_id, text=answer, reply_markup=keyboard)
                    return
            product = products_price.get(amount)
            if not renewal_keys(int(key_id), product):
                await bot.send_message(chat_id=telegram_id, text=answer_error, reply_markup=keyboard)

            answer = f"✅ Вы успешно продлили \"<b>Ключ № {key_id}</b>\" "
            keyboard = in_main_menu()
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
            await bot.send_photo(chat_id=telegram_id,
                                 photo=file_ids['renewal_ok'],
                                 caption=answer,
                                 reply_markup=keyboard,
                                 parse_mode="HTML")

            await state.finish()

    except Exception as e:
        logger.error(f"ERROR:Ошибка при оплате покупки или продления, user - {user_info}, ошибка - {e}")
        await bot.send_message(telegram_id, answer_error, reply_markup=main_menu_inline())
        await bot.send_message(err_send,
                               f"ERROR:Ошибка при оплате покупки или продления, user - {user_info}, ошибка - {e}")
