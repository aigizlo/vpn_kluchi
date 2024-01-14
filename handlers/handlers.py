from create_pay_links import generate_any_pay_link, generate_fropay_link
from text import *
from aiogram.dispatcher import FSMContext
from logger import logger

import asyncio

from config import dp, bot, err_send, one_month, three_month, one_year, secret_key, tg_channel
from balance import pay_from_personal_balance, add_referral_bonus, creating_payment
from keyboards.keyboards import *
from logic_keys.add_keys import add_keys, keys_send, add_free_keys
from logic_keys.renewal_keys import renewal_keys
from states import MyStates
from user_data import UserData, check_user_in_system
from balance import money_back

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
    '🇱🇺Нидерланды – Амстердам': 1,
    '🇩🇪Германия – Франкфурт': 2,
    '🇰🇿Казахстан – Астана': 3,
    '🇷🇺Россия – Санкт-Петербург': 4,
    '🇹🇷Турция – Стамбул': 5,
    '🇺🇸Америка – Лос Анджелес': 6}

keyboards_from_server_id = {
    1: 'amsterdam',
    2: 'germany',
    3: 'kz',
    4: 'russia',
    5: 'turkey',
    6: 'usa',
}

server_id_country = {
    1: '🇱🇺Нидерланды Амстердам',
    2: '🇩🇪Германия Франкфурт',
    3: '🇰🇿Казахстан Астана',
    4: '🇷🇺Россия',
    5: '🇹🇷Турция Стамбул',
    6: '🇺🇸Америка Лос Анджелес'
}


# обрабатываем нажатие кнопки "Получить ключ"
@dp.callback_query_handler(lambda c: c.data == "get_keys", state="*")
async def get_key_command(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.message.chat.id

    if callback_query.message.message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id)

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
    # cur_state = await state.get_state()

    await state.set_state(MyStates.payment_method)

    logger.info(f"Получить ключ, user_id - {user_info}")

    with open('images/tarrif.jpeg', 'rb') as photo:
        await bot.send_photo(chat_id=telegram_id,
                             photo=photo,
                             caption=answer,
                             reply_markup=keyboard)

    # await bot.send_message(chat_id=callback_query.message.chat.id, text=answer, reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('payment_method:'),
                           state=MyStates.payment_method)
async def process_callback_payment_method(callback_query: types.CallbackQuery, state='*'):

    user_info = user_data.get_userid_firsname_nickname(callback_query.message.chat.id)

    user_id = user_info[0]

    telegram_id = callback_query.message.chat.id

    if callback_query.message.message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id,
                                 message_id=telegram_id)

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

    with open('images/bill.jpeg', 'rb') as photo:
        message = await bot.send_photo(chat_id=telegram_id,
                             photo=photo,
                             caption=answer,
                             reply_markup=keyboard)

        print(message)

        # Асинхронная задержка перед удалением сообщения
        await asyncio.sleep(60)
        # Удаление сообщения после задержки
        await bot.delete_message(telegram_id, message.message.message_id)

# inline кнопка "Отмена"
@dp.callback_query_handler(lambda c: c.data == "go_back", state="*")
async def process_callback_go_back(callback_query: types.CallbackQuery):
    if callback_query.message.message_id:
        await bot.delete_message(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.chat.id)

    user_info = user_data.get_userid_firsname_nickname(callback_query.message.chat.id)

    with open('images/menu.jpeg', 'rb') as photo:
        await bot.send_photo(chat_id=callback_query.message.chat.id,
                             photo=photo,
                             caption=instruction,
                             parse_mode="HTML",
                             reply_markup=main_menu_inline())

    logger.info(f"Отмена - user - {user_info}")


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

            if callback_query.message.message_id:
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.chat.id)




        else:
            if callback_query.message.message_id:
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.chat.id)
    else:
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=answer,
                               reply_markup=subscribe_keyboard)


#
@dp.callback_query_handler(lambda c: c.data == "subscribe_ago", state="*")
async def check_subscription(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)
    telegram_id = callback_query.from_user.id

    answer = """🎁 <b>ПОДАРОК ДЛЯ ВАС </b>🎁

✅ Подпишитесь на канал и получите 3 дня пользования ключом БЕСПЛАТНО! 
"""


    try:
        User_Data = UserData()

        user_id = User_Data.get_user_id(telegram_id)

        with open('images/present.jpeg', 'rb') as photo:
            await bot.send_photo(chat_id=telegram_id,
                                 photo=photo,
                                 caption=answer,
                                 parse_mode="HTML",
                                 reply_markup=subscribe())

        # Выясняем, есть пользовался ли юзер бесплатным тарифом
        # use_free_tariff = User_Data.free_tariff_tg(telegram_id)
        # chat_member = await bot.get_chat_member(chat_id="@off_radar",
        #                                         user_id=telegram_id)

        # if chat_member.status in ["member", "administrator", "creator", "owner"]:
        #     if use_free_tariff == "UNUSED":
        #         await bot.send_message(chat_id=callback_query.from_user.id,
        #                                text="Благодарим за подписку, пожалуйста, вот ваш подарок",
        #                                reply_markup=kb_free_tariff)
        #         await bot.delete_message(chat_id=callback_query.message.chat.id,
        #                                  message_id=callback_query.message.message_id)
        #     else:
        #         await bot.delete_message(chat_id=callback_query.message.chat.id,
        #                                  message_id=callback_query.message.message_id)
        # else:
        #     await bot.send_message(chat_id=callback_query.message.chat.id,
        #                            text="Вы не подписаны на канал!",
        #                            reply_markup=subscribe_keyboard)
    except Exception as e:
        logger.error(f'ERROR:PROCESSО - check_subscription - Ошибка при проверке на подписку {user_id}: {e}')
        await bot.send_message(err_send, f'ERROR:PROCESSО - check_subscription - Ошибка при проверке на подписку {user_id}: {e}')


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


@dp.message_handler(commands=['help'], state="*")
async def my_info(message: types.Message):
    await message.reply(f"По всем вопросам - {support}")


@dp.message_handler(commands=['instruction'], state="*")
async def my_info(message: types.Message):
    await message.reply(instruction, parse_mode="HTML", disable_web_page_preview=True)
