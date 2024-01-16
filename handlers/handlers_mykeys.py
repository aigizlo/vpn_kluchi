import aiogram
from aiogram.dispatcher import FSMContext
import asyncio
from create_pay_links import generate_fropay_link, generate_any_pay_link
from logger import logger
from text import answer_not_keys

from config import dp, bot, err_send, one_month, one_year, three_month, secret_key
from balance import creating_payment, creating_payment_for_renewal
from keyboards.keyboards import *
from logic_keys.add_keys import keys_send
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

    # ищем юзер_айди пользовател
    try:
        user_id = user_data.get_user_id(telegram_id)
        # получаем список имен ключей
        key_ids = user_data.get_key_ids(user_id)
        # создаем 2 клавиатуры 1 c кнопкой "Назад" и 'Продлить ключи' если ключи есть у пользователя 2ую - если ключи есть
        keyboard = keyboard_if_have_keys()

        keyboard_not_keys = keyboard_if_not_keys()

        # список всех ключей с названием и датой работы
        try:
            keys = user_data.get_user_keys_info(user_id)

            answer = keys_send(keys)

            if not answer:
                answer = answer_not_keys

            logger.info(f"Мои ключи user - {user_info}")

            # выбор клавиатуры в зависимости от условия
            reply_keyboard = keyboard_not_keys if key_ids == [] else keyboard

            with open('images/my_keys.jpeg', 'rb') as photo:
                await bot.send_photo(chat_id=telegram_id,
                                     photo=photo,
                                     caption=answer,
                                     parse_mode="HTML",
                                     reply_markup=reply_keyboard)

        except Exception as e:
            logger.error(f"{e}")
    except Exception as e:
        logger.error(f"ERROR:Мои ключи, user - {user_info}, ошибка - {e}")
        # await message.answer(answer_error, reply_markup=main_menu())


# Продлить ключи                                                              здесь ловим состояние
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('prolong_keys'), state='*')
async def prolong_key_command(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")
    # ищем юзер_айди пользователя
    try:
        user_id = user_info[0]
        # получаем список имен ключей
        key_ids = user_data.get_key_ids(user_id)

        if not key_ids:
            answer = "У вас нет ключей для их продления"
            keyboard = main_menu_inline()
            await bot.send_message(text=answer, chat_id=telegram_id, reply_markup=keyboard)
            return
        # если есть ключи, то генерируем кнопки с их названиями
        key_buttons = generate_key_buttons(key_ids)
        answer = "Выберите ключ, который хотите продлить :"
        logger.info(f"Продлить колючи user - {user_info}")

        # Первое сообщение с инлайн-клавиатурой

        with open('images/renewal.jpeg', 'rb') as photo:
            await bot.send_photo(chat_id=telegram_id,
                                 photo=photo,
                                 caption=answer,
                                 reply_markup=key_buttons)

    except Exception as e:
        logger.error(f"ERROR:Продлить ключи user - {user_info} ошибка - {e}")
        # await message.answer(answer_error, reply_markup=main_menu_inline())


# Выюираем какой ключ будет продлен
@dp.callback_query_handler(lambda c: c.data.startswith("select_key"), state='*')
async def process_select_key(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    try:
        # выбранный ключ для продления
        selected_key = callback_query.data.split(":")[1]

        # сохраняем этот ключ в память состояния
        await state.update_data(key_id=selected_key)
        # текущее состояние
        logger.info(f"Выбран ключ для продления - {selected_key}, user - {user_info}")

        # удаляем инлайн клавиатуру по выбору ключей
        try:
            if callback_query.message.message_id:
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.message_id)
        except aiogram.utils.exceptions.MessageCantBeDeleted:
            logger.info("Сообщение не может быть удалено.")

        # выводим клавиатуру, где юзер выбираем период продления
        keyboard = choice_renewal_period()

        answer = f"""Вы выбрали <b>{selected_key}</b>

⏳ Выберите период, на который хотите продлить ваш ключ:
"""

        with open('images/renewal.jpeg', 'rb') as photo:
            await bot.send_photo(chat_id=telegram_id,
                                 photo=photo,
                                 caption=answer,
                                 parse_mode='HTML',
                                 reply_markup=keyboard)

        # передаем данные в новое состояние
        await state.set_state(MyStates.state_key_for_renewal)

        # await bot.answer_callback_query(callback_query.id)

    except Exception as e:
        logger.error(f"ERROR: НЕ Выбран ключ для продления - {selected_key}, user - {user_info}, "
                     f"user - {telegram_id}, ошибка {e}")
        await bot.send_message(answer_error, reply_markup=main_menu_inline())


@dp.callback_query_handler(lambda c: c.data.startswith('renewal:'), state=MyStates.state_key_for_renewal)
async def renewal_process(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id

    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    # берем переменные от этого состояния
    user_data_state = await state.get_data()

    key_id = user_data_state["key_id"]

    try:
        # Получаем данные из callback_data, месяц
        price = int(callback_query.data.split(':')[1])

        user_id = user_info[0]

        # удаляем клавиатуру с выбором тарифа для продления
        try:
            if callback_query.message.message_id:
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.message_id)
        except aiogram.utils.exceptions.MessageCantBeDeleted:
            logger.info("Сообщение не может быть удалено.")
        await state.set_state(MyStates.pay_from_balance)

        logger.info(f"Продление ключа , user - {user_info} на сумму {price}")

        answer = f"Сумма покупки <b>{price}</b> рублей, выберите способ оплаты:"
        # -------------------------
        pay_id = creating_payment_for_renewal(price, user_id, key_id)

        desc = f'{user_id},{price},{pay_id}'

        any_pay_link = generate_any_pay_link(str(pay_id), desc, str(price), secret_key)
        # вставляем ссылку в инлайн кнопку

        # fropay_link = generate_fropay_link(str(pay_id), str(price))

        keyboard = kb_pay(price, any_pay_link)
        # ----------------------------------------
        with open('images/bill.jpeg', 'rb') as photo:
            message = await bot.send_photo(chat_id=telegram_id,
                                           photo=photo,
                                           caption=answer,
                                           parse_mode="HTML",
                                           reply_markup=keyboard)
            # Асинхронная задержка перед удалением сообщения
            await asyncio.sleep(60)

            # Удаление сообщения после задержки
            try:
                if callback_query.message.message_id:
                    await bot.delete_message(chat_id=callback_query.message.chat.id,
                                             message_id=callback_query.message.message_id)
            except aiogram.utils.exceptions.MessageCantBeDeleted:
                logger.info("Сообщение не может быть удалено.")

    except Exception as e:
        logger.error(f"ERROR:Ошибка при продлении ключа, user - {user_info}, ошибка - {e}")
        await bot.send_message(answer_error, reply_markup=main_menu_inline())
