from logger import logger

from aiogram.dispatcher import FSMContext
from config import dp, bot_name, support, bot
from keyboards.keyboards import *
from states import MyStates

from user_data import UserData, check_user_in_system

from text import ref_link

user_data = UserData()


# обрабатываем нажатие кнопки "Заработай с нами"

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('partners'), state='*')
async def process_partners_command(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.message.chat.id

    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)

    if not check_user_in_system(telegram_id):
        await bot.send_message(chat_id=telegram_id, text="Что бы начать работу с ботом используйте команду /start")
        return

    user_info = user_data.get_userid_firsname_nickname(telegram_id)

    # создаем клавиатуру с кнопкой "Назад"
    cur_state = await state.get_state()
    keyboard = back_and_withdraw_inline()

    try:
        user_id = user_info[0]

        referral_balance = user_data.get_user_balance_bonus(user_id)

        count_ref = user_data.count_referrals(user_id)

        text = ref_link(user_id, bot_name, count_ref, referral_balance)
        # отправляем сообщение с текстом "Главное меню" и клавиатурой с четырьмя кнопками
        await bot.send_message(chat_id=telegram_id, text=text, parse_mode='HTML', disable_web_page_preview=True,
                               reply_markup=keyboard)
        await state.set_state(MyStates.state_promo_my)
        logger.info(f"Партнерская программа, user - {user_info}, state - {cur_state}")

    except Exception as e:
        logger.error(f"BUTTON_ERROR: Партнерская программа, user - {user_info}, ошибка - {e}")


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('withdraw_bonus'), state='*')
async def bonus_balance(callback_query: types.CallbackQuery, state: FSMContext):
    telegram_id = callback_query.message.chat.id

    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)

    user_info = user_data.get_userid_firsname_nickname(telegram_id)
    try:
        user_id = user_info[0]
        balance = user_data.get_user_balance_bonus(user_id)

        answer = f"Вывод средств происходит в ручном режиме, пожалуйста, напишите в поддержку {support}"

        if balance < 200:
            answer = f"Ваш баланс: {balance} рублей\nВывод средств доступен от 200 рублей"

        logger.info(f"Запрос на вывод средств user - {user_info}")

        await bot.send_message(chat_id=telegram_id, text=answer, reply_markup=cancel())

    except Exception as e:
        logger.error(f"BUTTON_ERROR: Ошибка обработки 'Вывод средств', пользователь {telegram_id}, ошибка - {e}")
