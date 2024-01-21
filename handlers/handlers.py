import aiogram
from create_pay_links import generate_any_pay_link, generate_fropay_link
from text import *
from aiogram.dispatcher import FSMContext
from logger import logger
from config import dp, bot, err_send, secret_key, tg_channel, file_ids
from balance import creating_payment
from keyboards.keyboards import *
from logic_keys.add_keys import add_free_keys
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
    three_month: 93,
    one_year: 365
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
        logger.info(f"Получить ключ, user_id - {user_info}")
    except Exception as e:
        logger.error(f'ERROR - Получить ключ, user_id - {user_info} {e}')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('payment_method:'),
                           state=MyStates.payment_method)
async def process_callback_payment_method(callback_query: types.CallbackQuery, state='*'):
    user_info = user_data.get_userid_firsname_nickname(callback_query.message.chat.id)

    user_id = user_info[0]

    telegram_id = callback_query.message.chat.id

    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")

    price = callback_query.data.split(':')[1]  # получаем цену

    answer = '''🔑 Получите ключ к стабильному VPN без рекламы

👇 Выберите способ оплаты:'''

    await state.set_state(MyStates.pay_from_balance)

    # создаем неоплаченый платеж
    pay_id = creating_payment(price, user_id)

    desc = f'{user_id},{price},{pay_id}'

    any_pay_link = generate_any_pay_link(str(pay_id), desc, str(price), secret_key)
    # вставляем ссылку в инлайн кнопку

    fropay_link = generate_fropay_link(str(pay_id), str(price))
    keyboard = kb_pay(price, any_pay_link, fropay_link)
    try:
        await bot.send_photo(chat_id=telegram_id,
                             photo=file_ids["bill"],
                             caption=answer,
                             parse_mode="HTML",
                             reply_markup=keyboard)
        logger.info(f"Способ оплаты {user_info}")
    except Exception as e:
        logger.error(f'ERROR - Способ оплаты - {user_info}', {e})


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

    try:
        await bot.send_photo(chat_id=callback_query.message.chat.id,
                             photo=file_ids['menu'],
                             caption=instruction,
                             parse_mode="HTML",
                             reply_markup=main_menu_inline())
        logger.info(f"Отмена - user - {user_info}")
    except Exception as e:
        logger.error(f'ERROR - Отмена - {user_info}', {e})





@dp.callback_query_handler(lambda c: c.data == "subscribe_check", state="*")
async def subscribe_no_thanks(callback_query: types.CallbackQuery):
    User_Data = UserData()
    telegram_id = callback_query.from_user.id

    user_id = User_Data.get_user_id(telegram_id)

    answer = '''Вы не подписаны на канал!

✅ Подпишитесь на канал и получите 3 дня пользования ключом БЕСПЛАТНО! 
'''

    subscribe_keyboard = subscribe()

    # Выясняем, есть пользовался ли юзер бесплатным тарифом
    use_free_tariff = User_Data.free_tariff_tg(telegram_id)
    chat_member = await bot.get_chat_member(chat_id=tg_channel,
                                            user_id=telegram_id)

    if chat_member.status in ["member", "administrator", "creator", "owner"]:
        if use_free_tariff == "UNUSED":

            key_value, server_id = add_free_keys(user_id)

            answer = text_free_tariff(server_id, key_value)

            User_Data.change_free_tariff(user_id, 1)

            # Обновляем данные об использовании бесплатного тарифа

            await bot.send_message(chat_id=callback_query.from_user.id,
                                   text=answer, reply_markup=main_menu_inline(),
                                   parse_mode="HTML", disable_web_page_preview=True)

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


#
@dp.callback_query_handler(lambda c: c.data == "subscribe_ago", state="*")
async def check_subscription(callback_query: types.CallbackQuery):
    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info("Сообщение не может быть удалено.")
    telegram_id = callback_query.from_user.id

    answer = """🎁 <b>ПОДАРОК ДЛЯ ВАС </b>🎁

✅ Подпишитесь на канал и получите 3 дня пользования ключом БЕСПЛАТНО! 
"""

    try:
        User_Data = UserData()

        user_id = User_Data.get_user_id(telegram_id)

        await bot.send_photo(chat_id=telegram_id,
                             photo=file_ids['present'],
                             caption=answer,
                             parse_mode="HTML",
                             reply_markup=subscribe())

    except Exception as e:
        logger.error(f'ERROR:PROCESSО - check_subscription - Ошибка при проверке на подписку {user_id}: {e}')
        await bot.send_message(err_send,
                               f'ERROR:PROCESSО - check_subscription - Ошибка при проверке на подписку {user_id}: {e}')


# @dp.callback_query_handler(lambda c: c.data == "", state="*")
# async def check_subscription(callback_query: types.CallbackQuery):

@dp.message_handler(commands=['my_info'], state="*")
async def my_info(message: types.Message):
    try:
        user_info = user_data.get_userid_firsname_nickname(message.from_user.id)

        user_id = user_info[0]

        all_info = user_data.get_user_info(user_id)

        txt_user_id = f"Мой user_id : {user_id}\n"

        answer = txt_user_id + all_info

        await message.reply(answer, disable_web_page_preview=True,
                            parse_mode="HTML")
        logger.info(f"my_info command - user {user_id}")

    except Exception as e:
        logger.info(f"COMMAND_ERROR - /my_info, {e}")
        await message.reply(f"Произошла ошибка при получении информации о пользователе .{e}")


@dp.callback_query_handler(lambda c: c.data == "why_we", state="*")
async def subscribe_no_thanks(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_userid_firsname_nickname(telegram_id)

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
                             reply_markup=main_menu_inline())

        logger.info(f"Почему мы ? {user_info}")
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.error(f"Ошибка при нажатии на Почему мы? - {user_info}")


@dp.callback_query_handler(lambda c: c.data == "video_inst", state="*")
async def subscribe_no_thanks(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    try:
        if callback_query.message.message_id:
            await bot.delete_message(chat_id=callback_query.message.chat.id,
                                     message_id=callback_query.message.message_id)
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        logger.info(f"Сообщение не может быть удалено. {user_info}")

    try:
        await bot.send_video(chat_id=callback_query.message.chat.id,
                             video=file_ids['video'],
                             caption=instruction,
                             parse_mode="HTML",
                             reply_markup=main_menu_inline2())
        logger.info(f"Видео инструкция - {user_info}")
    except Exception as e:
        logger.error(f"ERROR - Видео инструкция - {user_info}, {e}")


@dp.message_handler(content_types=['photo', 'video', 'document'])
async def handle_docs_photo(message: types.Message):
    # Получаем подпись, если она есть
    caption = message.caption if message.caption else "No caption"

    # Обработка фото
    if message.photo:
        photo_id = message.photo[-1].file_id  # Берем file_id самой большой версии фото
        logger.info(f"Photo ID: {photo_id}, Caption: {caption}")
        # Здесь вы можете сохранить photo_id и caption в файл или базу данных

    # Обработка видео
    elif message.video:
        video_id = message.video.file_id
        logger.info(f"Video ID: {video_id}, Caption: {caption}")


@dp.message_handler(commands=['help'], state="*")
async def my_info(message: types.Message):
    await message.reply(f"По всем вопросам - {support}")


@dp.message_handler(commands=['instruction'], state="*")
async def my_info(message: types.Message):
    await message.reply(instruction, parse_mode="HTML", disable_web_page_preview=True)
