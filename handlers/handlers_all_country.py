from logger import logger
import re

from config import dp
from aiogram.dispatcher import FSMContext

from handlers.handlers import MyStates
from logic_keys.add_keys import check_names

from keyboards.keyboards import *
from text import subscription_prompt, ask_server_name, ask_server_name_2, ask_server_name_3, \
    ask_server_name_4, payment_amount_prompt, all_country, answer_error, instruction
from user_data import UserData

# Паттерн для проверки допустимых символов
allowed_characters_pattern = r"^[a-zA-Zа-яА-Я0-9\s]+$"

country_server_id = {
    '🇱🇺Нидерланды – Амстердам': 1,
    '🇩🇪Германия – Франкфурт': 2,
    '🇰🇿Казахстан – Астана': 3,
    '🇷🇺Россия – Санкт-Петербург': 4,
    '🇹🇷Турция – Стамбул': 5
}

keyboards_from_server_id = {
    1: 'amsterdam',
    2: 'germany',
    3: 'kz',
    4: 'russia',
    5: 'turkey'
}

user_data = UserData()


# обрабатываем нажатие на какую либо страну
@dp.message_handler(lambda message: message.text in country_server_id, state='*')
async def select_country(message: types.Message, state: FSMContext):
    try:
        server_id = country_server_id.get(message.text)
        # определяем какую клаву отправляем в зависимости от country
        country = keyboards_from_server_id.get(server_id)
        keyboard = generate_tariff_keyboard(country)
        await state.update_data(server=server_id)
        # отлов состояния state_tarrif
        await state.set_state(MyStates.state_tarrif)
        await message.answer(subscription_prompt, reply_markup=keyboard)
        logger.info(
            f"PROCESS:select_country, user - {message.from_user.id} server - {server_id}")

    except Exception as e:
        await message.answer(answer_error, reply_markup=main_menu())
        logger.error(f"ERROR:select_country, user - {message.from_user.id},, ошибка - {e}")


# выбор тарифа (выбор периода)
@dp.message_handler(lambda message: message.text in all_country,
                    state=MyStates.state_tarrif)
async def select_tariff(message: types.Message, state: FSMContext):
    # кнопка назад
    keyboard = back_button()

    telegram_id = message.from_user.id

    try:
        amount = int(message.text.split(" — ")[-1].split(" ")[0])  # Извлекаем сумму из текста

        # обновляем данные состояния
        await state.update_data(amount=amount)
        # отлов следующего состояния
        await state.set_state(MyStates.state_key_name)
        # спрашиваем название для сервера юзера
        await message.answer(ask_server_name, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"ERROR:select_tariff, user - {telegram_id}, ошибка - {e}")
        await message.answer(answer_error, reply_markup=keyboard)


# спрашиваем имя сервера
@dp.message_handler(state=MyStates.state_key_name)
async def process_key_name(message: types.Message, state: FSMContext):
    # это класс, для быстрого получения данных
    User_Data = UserData()
    # сохраняем название сервра юзера в переменную
    key_name = message.text
    telegram_id = message.from_user.id
    # ищем его user_id
    try:
        user_id = User_Data.get_user_id(telegram_id)
        # здесь все переменные состояния
        user_data_state = await state.get_data()
        amount = user_data_state["amount"]
        # возвращаем в глав меню есл нажали НАЗАД
        if message.text == '🔙Назад':
            keyboard = main_menu()
            await message.answer("Главное меню:/n" + instruction, parse_mode="HTML", reply_markup=keyboard)
            await state.finish()
            return
        # если имя длинное - переспрашиваем
        if len(key_name) > 35:
            await message.answer(ask_server_name_2)
            return
        # проверяем на повторность имени у конкретного юзера
        if check_names(user_id, key_name):
            await message.answer(ask_server_name_3)
            return
        # исключаем любые другие символы кроме букв и цифр
        if not re.match(allowed_characters_pattern, key_name):
            await message.answer(ask_server_name_4)
            return
        # обновляем переменные состояния для передачи их дальше
        await state.update_data(key_name=key_name, action="pay")

        # спрашиваем способ оплаты и показываем сумму
        answer = payment_amount_prompt(amount)

        # показываем инлайн клаву для выбора способа оплаты
        pay_keyboard = get_pay_method_keyboard()

        await message.answer(answer, parse_mode='HTML', reply_markup=pay_keyboard)
        # отлов состояния pay_from_balance
        await state.set_state(MyStates.pay_from_balance)

        logger.info(f"PROCESS:process_key_name, user - {telegram_id}")
    except Exception as e:
        logger.info(f"ERROR:process_key_name, user - {telegram_id}, {e}")
        await message.answer(answer_error, reply_markup=main_menu())
