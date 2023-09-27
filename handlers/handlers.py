from aiogram.types import callback_query

from logs.logger import logger
from aiogram.dispatcher import FSMContext

from logic_keys.add_keys import add_keys
from user_data import UserData, check_user_in_system
from db_conn.get_conn import create_connection
from config import dp, bot, err_send, support
from keyboards.keyboards import *
from states import MyStates
from text import answer_error, offer_free_plan, text_free_tariff, instruction, offer_free_plan_2



user_data = UserData()

server_id_country = {
    1: 'Нидерланды Амстердам',
    2: 'Германия Франкфурт',
    3: 'Казахстан Астана',
    4: 'Россия',
    5: 'Турция Стамбул'
}

main_menu_handlers = ['🔐Получить ключ', '🔙Назад', '🔑Мои ключи', '💰Баланс', '💵Партнерская программа']


# @dp.message_handler(lambda message: message.text in main_menu_handlers, state="*")
# async def get_key_command(message: types.Message, state: FSMContext):


# обрабатываем нажатие кнопки "Получить ключ"
@dp.message_handler(lambda message: message.text == '🔐Получить ключ', state="*")
async def get_key_command(message: types.Message, state: FSMContext):

    if not check_user_in_system(message.from_user.id):
        await message.answer("Что бы начать работу с ботом используйте команду /start")
        return

    # импортируем кливатуру

    keyboard = kb_servers()
    answer = "Выберите страну:"
    # cur_state = await state.get_state()
    await state.set_state(MyStates.state_get_keys)

    logger.info(f"PROCESS:get_key_command, user - {message.from_user.id}")

    await message.answer(answer, reply_markup=keyboard)


# обрабатываем нажатие кнопки "Назад"
@dp.message_handler(lambda message: message.text == '🔙Назад', state='*')
async def back_command(message: types.Message, state: FSMContext):

    if not check_user_in_system(message.from_user.id):
        await message.answer("Что бы начать работу с ботом используйте команду /start")
        return
    # создаем клавиатуру с четырьмя кнопками
    states = [MyStates.state_get_keys, MyStates.state_my_keys]
    cur_state = await state.get_state()
    User_Data = UserData()
    keyboard = main_menu()
    logger.info(f"PROCESS:back_command, user - {message.from_user.id}")
    if cur_state in states:
        await message.answer("Главное меню",
                             reply_markup=keyboard)
        await state.finish()

    else:
        await message.answer(instruction, disable_web_page_preview=True,
                             parse_mode='HTML',
                             reply_markup=keyboard)

    try:
        # здесь проверем подписку и использование бесплатного тарифа
        user_id = User_Data.get_user_id(message.from_user.id)
        # сhat_member = await bot.get_chat_member(chat_id="@off_radar", user_id=message.from_user.id)
        # # проверяем, что он не состоит в группе
        # if сhat_member.status not in ["creator", "administrator", "member", "restricted"]:
        #     if user_id:
        #         # проверяем использовал ли он бесплатный тариф
        #         if User_Data.free_tariff(user_id) == "UNUSED":
        #             await message.answer(offer_free_plan, reply_markup=subscribe())
        #             return

        if user_id:
            # проверяем использовал ли он бесплатный тариф
            if User_Data.free_tariff(user_id) == "UNUSED":
                await message.answer(offer_free_plan_2, reply_markup=free_tariff())
    except Exception as e:
        logger.error(f"ERROR:back_command, user - {message.from_user.id}, ошибка - {e}")
        answer = answer_error
        await message.answer(answer, reply_markup=keyboard)
        await bot.send_message(err_send, f"Ошибка при нажатии НАЗАД - {e}, пользователь {user_id}")
    await state.finish()


# inline кнопка "Отмена"
@dp.callback_query_handler(lambda c: c.data == "go_back", state="*")
async def process_callback_go_back(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    # Удаляем предыдущее сообщение с инлайн-клавиатурой
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)

    # main_menu_keyboard = main_menu()


@dp.callback_query_handler(lambda c: c.data == "free_tariff", state="*")
async def free_tariff_select_location(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    # Удаляем предыдущее сообщение с инлайн-клавиатурой
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)

    keyboard = choice_location_free_tariff()

    # Отправляем новое сообщение с обычной клавиатурой
    await bot.send_message(chat_id=callback_query.message.chat.id,
                           text="Выберите локацию:",
                           reply_markup=keyboard)
    logger.info(f"PROCESS:free_tariff, user - {callback_query.message.chat.id}")


# обрабатываем кнопку выбора локации для бесплатного тарифного плана
@dp.callback_query_handler(lambda c: c.data.startswith('free_select_country:'), state='*')
async def choice_free_tariff(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    # забираем сервер
    server_id = int(callback_query.data.split(':')[1])

    # сохраняем его в текущим состоянии
    await state.update_data(server=server_id)

    main_menu_keyboard = main_menu()
    # название страны по номеру сервера
    location = server_id_country.get(server_id)

    try:
        User_Data = UserData()
        # берем его user_id
        user_id = User_Data.get_user_id(callback_query.message.chat.id)

        # названия локации сервера передаем в название сервера
        key_name = location.replace("-", r"\-")

        use_free_tarrif = User_Data.free_tariff(user_id)

        if not use_free_tarrif:
            await bot.send_message(callback_query.message.chat.id, answer_error)
            return

        if use_free_tarrif == "USED":
            answer = "Вы уже использовали бесплатный тариф на 14 дней"

        # проверяем был ли он у него уже
        if use_free_tarrif == "UNUSED":
            key_id = await add_keys(server_id, user_id, key_name, 14)

            if key_id:
                key_value = User_Data.get_key_value(key_id)
                answer = text_free_tariff(location, key_value)
                User_Data.change_free_tariff(user_id, 1)
            else:
                answer = answer_error

        # Удаляем предыдущее сообщение с инлайн-клавиатурой
        await bot.delete_message(chat_id=callback_query.message.chat.id,
                                 message_id=callback_query.message.message_id)

        # Отправляем новое сообщение с обычной клавиатурой
        await bot.send_message(chat_id=callback_query.message.chat.id,
                               text=answer,
                               parse_mode="HTML",
                               disable_web_page_preview=True,
                               reply_markup=main_menu_keyboard)

        logger.info(f"PROCESS:choice_free_tariff, user - {callback_query.message.chat.id}")

    except Exception as e:
        logger.error(f"ERROR:choice_tariff, user - {callback_query.message.chat.id}, Ошбика {e}")
        await bot.send_message(callback_query.message.chat.id, answer_error)
        await bot.send_message(err_send, f"ошибка в процессе choice_free_tariff {e}, user - {user_id}")


@dp.callback_query_handler(lambda c: c.data == "subscribe_no_thanks", state="*")
async def subscribe_no_thanks(callback_query: types.CallbackQuery):
    User_Data = UserData()
    user_id = User_Data.get_user_id(callback_query.message.chat.id)
    User_Data.change_free_tariff(user_id, 2, )
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.message.chat.id, "Вы отказались от акции")


@dp.callback_query_handler(lambda c: c.data == "subscribe_ago", state="*")
async def check_subscription(callback_query: types.CallbackQuery):
    telegram_id = callback_query.from_user.id
    subscribe_keyboard = subscribe()
    kb_free_tariff = free_tariff()

    try:
        User_Data = UserData()

        user_id = User_Data.get_user_id(telegram_id)
        # Выясняем, есть пользовался ли юзер бесплатным тарифом
        use_free_tariff = User_Data.free_tariff_tg(telegram_id)
        print(use_free_tariff)
        chat_member = await bot.get_chat_member(chat_id="@off_radar",
                                                user_id=telegram_id)

        if chat_member.status in ["member", "administrator", "creator", "owner"]:
            if use_free_tariff == "UNUSED":
                await bot.send_message(chat_id=callback_query.from_user.id,
                                       text="Благодарим за подписку, пожалуйста, вот ваш подарок",
                                       reply_markup=kb_free_tariff)
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.message_id)
            else:
                await bot.delete_message(chat_id=callback_query.message.chat.id,
                                         message_id=callback_query.message.message_id)
        else:
            await bot.send_message(chat_id=callback_query.message.chat.id,
                                   text="Вы не подписаны на канал!",
                                   reply_markup=subscribe_keyboard)
    except Exception as e:
        logger.error(f'ERROR:PROCESSО - check_subscription - Ошибка при проверке на подписку {user_id}: {e}')
        await bot.send_message(err_send, f'ERROR:PROCESSО - check_subscription - Ошибка при проверке на подписку {user_id}: {e}')


@dp.message_handler(commands=['my_info'], state="*")
async def my_info(message: types.Message):
    try:

        User_Data = UserData()

        user_id = User_Data.get_user_id(message.from_user.id)

        all_info = User_Data.get_user_info(user_id)

        txt_user_id = f"Мой user_id : {user_id}\n"

        answer = txt_user_id + all_info

        await message.reply(answer, disable_web_page_preview=True,
                            parse_mode="HTML")

    except Exception as e:
        logger.info(f"COMMAND_ERROR - /my_info, {e}")
        await message.reply(f"Произошла ошибка при получении информации о пользователе .{e}")


@dp.message_handler(commands=['help'], state="*")
async def my_info(message: types.Message):
    await message.reply(f"По всем вопросам - {support}")