from logs.logger import logger

from aiogram.dispatcher import FSMContext
from config import dp, bot_name, support
from keyboards.keyboards import *
from states import MyStates

from user_data import UserData, check_user_in_system

from text import ref_link


# обрабатываем нажатие кнопки "Партнерская программа"
@dp.message_handler(lambda message: message.text == '💵Партнерская программа', state="*")
async def process_partners_command(message: types.Message, state: FSMContext):
    if not check_user_in_system(message.from_user.id):
        await message.answer("Что бы начать работу с ботом используйте команду /start")
        return
    # создаем клавиатуру с кнопкой "Назад"
    user_data = UserData()
    cur_state = await state.get_state()
    keyboard = back_and_withdraw()

    telegram_id = message.from_user.id
    try:
        user_id = user_data.get_user_id(telegram_id)

        referral_balance = user_data.get_user_balance_bonus(user_id)

        count_ref = user_data.count_referrals(user_id)

        text = ref_link(user_id, bot_name, count_ref, referral_balance)
        # отправляем сообщение с текстом "Главное меню" и клавиатурой с четырьмя кнопками
        await message.answer(text, parse_mode='HTML', disable_web_page_preview=True, reply_markup=keyboard)
        await state.set_state(MyStates.state_promo_my)
        logger.info(f"BUTTON: Партнерская программа, user - {telegram_id}, state - {cur_state}")

    except Exception as e:
        logger.error(f"BUTTON_ERROR: Партнерская программа, user - {telegram_id}, ошибка - {e}")


@dp.message_handler(lambda message: message.text == 'Вывод средств', state=MyStates.state_promo_my)
async def bonus_balance(message: types.Message):
    keyboard = back_button()
    user_data = UserData()
    telegram_id = message.from_user.id
    try:

        user_id = user_data.get_user_id(telegram_id)
        balance = user_data.get_user_balance_bonus(user_id)

        answer = f"Вывод средств происходит в ручном режиме, пожалуйста, напишите в поддержку {support}"

        if balance < 500:
            answer = f"Ваш баланс: {balance} рублей\nВывод средств доступен от 500 рублей"

        await message.answer(answer, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"BUTTON_ERROR: Ошибка обработки 'Вывод средств', пользователь {telegram_id}, ошибка - {e}")
