import aiogram
from aiogram.utils.exceptions import TelegramAPIError
from config import products

from create_pay_links import generate_any_pay_link, generate_free_kassa, create_order
from text import *
from aiogram.dispatcher import FSMContext
from logger import logger
from config import dp, bot, err_send, secret_key, tg_channel, file_ids, admin, one_month_sale, three_month_sale
from balance import creating_payment
from keyboards.keyboards import *
from logic_keys.add_keys import add_free_keys, keys_send
from states import MyStates
from user_data import UserData, check_user_in_system

video_id = None

user_data = UserData()
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


amount_to_days = {
    one_month: 31,
    one_month_sale: 31,
    three_month: 93,
    three_month_sale: 93,
    one_year: 365,
}

price_to_month = {
    one_month: 1,
    one_month_sale: 1,
    three_month: 3,
    three_month_sale: 3,
    one_year: 12
}
#


country_server_id = {
    '🇩🇪Германия – Франкфурт': 1,
    '🇺🇸Америка – Лос Анджелес': 2}

server_id_country = {
    1: '🇩🇪Германия Франкфурт',
    2: '🇺🇸Америка Лос Анджелес'
}


# обрабатываем нажатие кнопки "Получить ключ"
@dp.callback_query_handler(lambda c: c.data == "get_keys", state="*")
async def get_key_command(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.message.chat.id

    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")

    if not check_user_in_system(callback_query.message.chat.id):
        await bot.send_message(chat_id=telegram_id,
                               text='Что бы начать работу с ботом используйте команду /start')
        return
    user_info = user_data.get_userid_firsname_nickname(callback_query.message.chat.id)

    user_id = user_info[0]

    # обновляем последнее дествие польщзователя
    user_data.update_last_activity(user_id)

    free_tarrif = user_data.free_tariff(user_id)

    # импортируем кливатуру
    keyboard = choice_period_not_free()

    if free_tarrif == "UNUSED":
        keyboard = choice_period()

    answer = "Выберите тариф:"

    await state.set_state(MyStates.payment_method)

    try:
        await bot.send_photo(chat_id=telegram_id,
                             photo=file_ids["tarrif"],
                             caption=answer,
                             reply_markup=keyboard)
        logger.info(f"BUTTON:get_key, user_id - {user_info}")
    except Exception as e:
        logger.error(f'ERROR - BUTTON:get_key, user_id - {user_info} {e}')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('payment_method:'),
                           state=MyStates.payment_method)
async def process_callback_payment_method(callback_query: types.CallbackQuery, state='*'):
    user_info = user_data.get_userid_firsname_nickname(callback_query.message.chat.id)

    user_id = user_info[0]

    # обновляем последнее дествие польщзователя
    user_data.update_last_activity(user_id)

    telegram_id = callback_query.message.chat.id

    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")

    price = int(callback_query.data.split(':')[1])  # получаем цену

    month = price_to_month.get(price)

    answer = '''🔑 Получите ключ к стабильному VPN без рекламы 
👇 Выберите способ оплаты:'''

    await state.set_state(MyStates.pay_from_balance)

    # создаем неоплаченый платеж
    pay_id = creating_payment(price, user_id)

    print(month)
    print(type(month))

    print(products.get(month))

    order_link = create_order(products.get(month), pay_id)
    # any_pay_link = generate_any_pay_link(str(pay_id), desc, str(price), secret_key)
    #
    # fk_link = generate_free_kassa(str(pay_id), str(price))
    # product = pro
    # pay_link = create_order(products.get(month), str(pay_id))
    await state.update_data(user_id=user_id, action='pay', month=month,
                            amount=int(price), pay_id=pay_id, fk_link=order_link)

    await state.set_state(MyStates.pay_from_balance)

    keyboard = kb_pay(price, order_link)

    try:
        await bot.send_photo(chat_id=telegram_id,
                             photo=file_ids["bill"],
                             caption=answer,
                             parse_mode="HTML",
                             reply_markup=keyboard)
        logger.info(f"BUTTON - payment_method {user_info}")
    except Exception as e:
        logger.error(f'ERROR - BUTTON:payment_method - {user_info}', {e})


# inline кнопка "Отмена"
@dp.callback_query_handler(lambda c: c.data == "go_back", state="*")
async def process_callback_go_back(callback_query: types.CallbackQuery):
    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")

    user_info = user_data.get_userid_firsname_nickname(callback_query.message.chat.id)
    user_id = user_info[0]

    # обновляем последнее действие пользователя
    user_data.update_last_activity(user_id)

    try:
        await bot.send_photo(chat_id=callback_query.message.chat.id,
                             photo=file_ids['menu'],
                             caption=instruction,
                             parse_mode="HTML",
                             reply_markup=main_menu_inline())
        logger.info(f"BUTTON:cancel - user - {user_info}")
    except Exception as e:
        logger.error(f'ERROR - BUTTON:cancel - {user_info}', {e})


@dp.callback_query_handler(lambda c: c.data == "subscribe_check", state="*")
async def subscribe_no_thanks(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_user_data(telegram_id)
    user_id = user_info.get("user_id")
    use_free_tariff = user_info.get("free_tariff")

    user_data.update_last_activity(user_id)

    answer = '''Вы не подписаны на канал!

✅ Подпишитесь на канал и получите 10 дней пользования ключом БЕСПЛАТНО! 
'''

    subscribe_keyboard = subscribe()

    chat_member = await bot.get_chat_member(chat_id=tg_channel,
                                            user_id=telegram_id)

    logger.info(f"BUTTON:subscribe_check user - {user_id}")

    if chat_member.status in ["member", "administrator", "creator", "owner"]:
        if use_free_tariff == 0:

            key_value, server_id = add_free_keys(user_id)

            answer = text_free_tariff(server_id)

            key_value = f'<code>{key_value}</code>'

            # Обновляем данные об использовании бесплатного тарифа
            user_data.change_free_tariff(user_id, 1)

            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=answer,
                                   parse_mode="HTML",
                                   disable_web_page_preview=True)
            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=key_value, reply_markup=in_main_menu(),
                                   parse_mode="HTML")
            logger.info(f"""BOT_SEND_TRAIL_KEY - {key_value} for user - {user_id, user_info.get("first_name")}""")

            try:
                if callback_query.message.message_id:
                    await bot.delete_message(chat_id=callback_query.message.chat.id,
                                             message_id=callback_query.message.message_id)
            except aiogram.utils.exceptions.MessageCantBeDeleted:
                logger.info("Сообщение не может быть удалено.")

        else:
            try:
                if callback_query.message.message_id:
                    await bot.delete_message(chat_id=callback_query.message.chat.id,
                                             message_id=callback_query.message.message_id)
            except aiogram.utils.exceptions.MessageCantBeDeleted:
                logger.info("Сообщение не может быть удалено.")
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=answer,
                               reply_markup=subscribe_keyboard)
        logger.info(f"user not subscribe tg channel")


#
@dp.callback_query_handler(lambda c: c.data == "get_present", state="*")
async def check_subscription(callback_query: types.CallbackQuery):
    user_info = user_data.get_userid_firsname_nickname(callback_query.from_user.id)
    user_id = user_info[0]

    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")
    telegram_id = callback_query.from_user.id

    # обновляем последнее действие пользователя
    user_data.update_last_activity(user_id)

    answer = """🎁 <b>ПОДАРОК ДЛЯ ВАС </b>🎁

✅ Подпишитесь на канал и получите 10 дней пользования ключом БЕСПЛАТНО! 
"""

    try:

        await bot.send_photo(chat_id=telegram_id,
                             photo=file_ids['present'],
                             caption=answer,
                             parse_mode="HTML",
                             reply_markup=subscribe())
        logger.info(f"BUTTON:get_present user - {user_info}")

    except Exception as e:
        logger.error(
            f'ERROR - BUTTON:get_present - check_subscription - Ошибка при проверке на подписку {user_id}: {e}')
        await bot.send_message(err_send,
                               f'ERROR - BUTTON:get_present - check_subscription - Ошибка при проверке на подписку {user_id}: {e}')


@dp.callback_query_handler(lambda c: c.data == "why_we", state="*")
async def subscribe_no_thanks(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    # обновляем последнее действие пользователя
    user_data.update_last_activity(user_info[0])

    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info(f"Сообщение не может быть удалено. {user_info}")

    try:
        await bot.send_photo(chat_id=telegram_id,
                             photo=file_ids["why_we"],
                             caption=why_we,
                             parse_mode="HTML",
                             reply_markup=cancel())

        logger.info(f"BUTTON:why_we {user_info}")
    except Exception as e:
        logger.error(f"ERROR - BUTTON:why_we - {user_info} , {e}")


@dp.callback_query_handler(lambda c: c.data == "video_inst", state="*")
async def subscribe_no_thanks(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    # обновляем последнее действие пользователя
    user_data.update_last_activity(user_info[0])
    try:
        await bot.send_video(chat_id=callback_query.message.chat.id,
                             video=file_ids['video'],
                             caption=instruction,
                             parse_mode="HTML",
                             reply_markup=cancel())
        logger.info(f"BUTTON:video_instruction {user_info}")
    except Exception as e:
        logger.error(f"ERROR - BUTTON:video_instruction - {user_info}, {e}")


@dp.message_handler(content_types=['photo', 'video', 'document'])
async def handle_docs_photo(message: types.Message):
    # Получаем подпись, если она есть
    caption = message.caption if message.caption else "No caption"

    user_info = user_data.get_userid_firsname_nickname(message.from_user.id)

    # Обработка фото
    if message.photo:
        photo_id = message.photo[-1].file_id  # Берем file_id самой большой версии фото

        await bot.send_photo(chat_id=err_send,
                             photo=photo_id,
                             caption=f"от {user_info}")

        logger.info(f"Photo ID: {photo_id}, Caption: {caption}, user - {user_info}")
        # Здесь вы можете сохранить photo_id и caption в файл или базу данных

    # Обработка видео
    elif message.video:
        video_id = message.video.file_id
        await bot.send_video(chat_id=err_send,
                             video=video_id,
                             caption=f"от {user_info}")

        logger.info(f"Video ID: {video_id}, Caption: {caption}, user - {user_info}")

    elif message.document:
        doc_id = message.document.file_id
        await bot.send_document(chat_id=err_send,
                                document=doc_id,
                                caption=f"от {user_info}")
        logger.info(f"Video ID: {doc_id}, Caption: {caption}, user - {user_info}")


@dp.callback_query_handler(lambda c: c.data == "main_menu", state="*")
async def main_menu(callback_query: types.CallbackQuery):
    await bot.send_photo(chat_id=callback_query.message.chat.id,
                         photo=file_ids['menu'],
                         caption=instruction,
                         parse_mode="HTML",
                         reply_markup=main_menu_inline())


@dp.callback_query_handler(lambda c: c.data == "get10days", state="*")
async def get10days(callback_query: types.CallbackQuery):
    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")

    telegram_id = callback_query.from_user.id

    user_info = user_data.get_user_data(telegram_id)

    user_id = user_info.get("user_id")

    # обновляем последнее действие пользователя
    user_data.update_last_activity(user_id)

    # Смотрим, брал ли он триал или нет
    if user_info.get("free_tariff") == 0:

        key_value, server_id = add_free_keys(user_id)

        answer = text_free_tariff(server_id)

        key_value2 = f'<code>{key_value}</code>'
        # Обновляем данные об использовании бесплатного тарифа

        user_data.change_free_tariff(user_id, 1)

        # Обновляем данные об использовании бесплатного тарифа

        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=answer,
                               parse_mode="HTML",
                               disable_web_page_preview=True)
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text=key_value2, reply_markup=in_main_menu(),
                               parse_mode="HTML")
        await bot.send_message(chat_id=err_send, text=f"user - {user_id} взял ключ на {10} дней", parse_mode="HTML")

        logger.info(f"""BOT_SEND_TRAIL_KEY - {key_value} for user - {user_info.get("user_id")}""")

        try:
            if callback_query.message.message_id:
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.message_id)
        except TelegramAPIError as e:
            logger.error(f"Произошла ошибка при удалении сообщения: {e}")

    else:
        await bot.send_message(chat_id=callback_query.from_user.id,
                               text="Вы уже взяли бесплатный ключ\n",
                               parse_mode="HTML",
                               disable_web_page_preview=True)
        try:
            if callback_query.message.message_id:
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.message_id)
        except TelegramAPIError as e:
            logger.error(f"Произошла ошибка при удалении сообщения: {e}")

    # await bot.send_message(chat_id=admin, text=f"user - {user_id} взял ключ на {10} дней ")

    #
    # try:
    #     if callback_query.message.message_id:
    #         await bot.delete_message(chat_id=callback_query.message.chat.id,
    #                                  message_id=callback_query.message.message_id)
    # except aiogram.utils.exceptions.MessageCantBeDeleted:
    #     logger.info("Сообщение не может быть удалено.")


@dp.message_handler(commands=['help'], state="*")
async def help_command(message: types.Message):
    info_user = user_data.get_user_data(message.from_user.id)

    user_id = info_user.get("user_id")
    await message.reply(f"Техническая поддержка - {support}\nв обращении ОБЯЗАТЕЛЬНО укажите ваш персональный id ("
                        f"user_id) - {user_id}")


@dp.message_handler(commands=['my_info'], state="*")
async def help_command(message: types.Message):
    user_info = user_data.get_userid_firsname_nickname(message.from_user.id)
    user_id = user_info[0]
    answer = user_data.get_user_info(user_id)
    keys = user_data.get_user_keys_info(user_id)
    if not keys:
        await message.answer(answer, parse_mode="HTML")
        return
    _keys = keys_send(keys)
    await message.answer(answer + '\n\n' + _keys, parse_mode='HTML', disable_web_page_preview=True)


@dp.message_handler(commands=['menu'], state="*")
async def main_menu(message: types.Message):
    await bot.send_photo(chat_id=message.from_user.id,
                         photo=file_ids['menu'],
                         caption=instruction,
                         parse_mode="HTML",
                         reply_markup=main_menu_inline())


@dp.message_handler(commands=['instruction'], state="*")
async def instruction_command(message: types.Message):
    await bot.send_video(chat_id=message.from_user.id,
                         video=file_ids['video'],
                         caption=instruction,
                         parse_mode="HTML",
                         reply_markup=main_menu_inline())


# @dp.message_handler(commands=['products'], state="*")
# async def instruction_command(message: types.Message):
#
#     from config import products
#
#     order_link = create_order(products.get(1), '173')
#     print(order_link)
#
#     await message.answer(order_link)


