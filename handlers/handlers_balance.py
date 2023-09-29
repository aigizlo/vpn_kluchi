from balance import generate_payment_url, creating_payment
from logger import logger
from aiogram.dispatcher import FSMContext
from config import dp, secret_key
from keyboards.keyboards import *
from states import MyStates
from text import answer_error
from user_data import UserData, check_user_in_system

user_data = UserData()


# обрабатываем нажатие кнопки "Баланс"
@dp.message_handler(lambda message: message.text == '💰Баланс', state='*')
async def balance_command(message: types.Message, state: FSMContext):
    if not check_user_in_system(message.from_user.id):
        await message.answer("Что бы начать работу с ботом используйте команду /start")
        return

    try:
        keyboard = balance_keyboard()

        # забираем из класса UserData
        user_id = user_data.get_user_id(message.from_user.id)

        await state.update_data(user_id=user_id)

        user_balance = user_data.get_user_balance_ops_by_user_id(user_id)

        answer2 = f"Ваш баланс {user_balance} рублей"

        logger.info(f"PROCESS:balance_command, user_id - {user_id}")
        # отправляем сообщение с текстом "Главное меню" и клавиатурой с четырьмя кнопками
        await state.set_state(MyStates.state_balance)
        await message.answer(answer2, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"ERROR:balance_command, user_id - {user_id}, error - {e}")
        await message.answer(answer_error, reply_markup=main_menu())


@dp.message_handler(lambda message: message.text == 'Пополнить баланс', state=MyStates.state_balance)
async def replenish_balance_comand(message: types.Message, state: FSMContext):
    await message.answer("Введите сумму (целое число без иных символом), которую хотите пополнить")
    await state.set_state(MyStates.state_replenish_balance)


@dp.message_handler(state=MyStates.state_replenish_balance)
async def get_amount(message: types.Message, state: FSMContext):
    amount_str = message.text

    user_data_state = await state.get_data()
    user_id = user_data_state["user_id"]

    amount = int(amount_str)
    pay_id = creating_payment(amount, user_id)

    try:

        if isinstance(amount, int):
            link = generate_payment_url(str(pay_id), str(amount), secret_key)
            keyboard = kb_pay(amount, link)
            await message.answer(f"Чтобы пополнить баланс на сумму {amount}, нажмите «Пополнить»",
                                 reply_markup=keyboard)
        else:
            await message.answer("Введенное значение не является целым числом.")
    except ValueError:
        await message.answer("Введенное значение не является числом.")

# # обрабатываем нажатие кнопки "Включить автопродление"
# @dp.message_handler(lambda message: message.text == 'Включить автопродление', state=MyStates.state_balance)
# async def balance_command(message: types.Message, state: FSMContext):
#     telegram_id = message.from_user.id
#     name_key = name_keys(telegram_id)
#
#     keyboard = generate_key_buttons(name_key)
#
#     keyboard_not_keys  = back_button()
#
#     # user_balance = balance(message.from_user.id)
#
#     answer_if_have_keys = "Выберите ключ, для которого, вы хотите включить авто-продление:"
#     answer_if_not_keys = "У вас нет активных ключей"
#     cur_state = await state.get_state()
#
#     reply_keyboard = keyboard_not_keys if name_key == [] else keyboard
#     text = answer_if_not_keys if name_key == [] else answer_if_have_keys
#     logging.info(f"Включить автопродление , state - {cur_state}")
#     # отправляем сообщение с текстом "Главное меню" и клавиатурой с четырьмя кнопками
#     await state.set_state(MyStates.state_balance)
#     await message.answer(text, reply_markup=reply_keyboard)
