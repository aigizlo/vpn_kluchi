from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class MyStates(FSMContext):

    # общее состояние для оплаты
    payment_method = 'payment_method'

    pay_from_balance = 'pay_from_balance'

    # cопровождение до оплаты
    state_amsterdam = 'state_amsterdam'
    state_tarrif = 'state_amsterdam_tarrif'
    state_key_name = 'state_amsterdam_key_name'

    # глав меню
    state_main_menu = 'state_main_menu'

    # нажатие кнопки Получить ключ для выбора серверов
    state_server_selection = 'state_server_selection'

    state_get_keys = 'state_get_keys'
    # мои ключи - продление ключей
    state_my_keys = 'state_my_keys'
    # key renewal
    state_key_renewal = 'state_key_renewal'
    # смена локации
    state_key_exchange = 'state_key_exchange'
    # выбор ключа
    state_key_for_renewal = 'state_key_for_renewal'
    # выбор оплаты
    state_key_for_renewal_1 = 'state_key_for_renewal_1'


    # balance
    state_balance = "state_balance"
    state_replenish_balance = "state_replenish_balance"
    state_send_pay_link = 'state_refill'




    state_choice_fee_tariff = 'state_choice_fee_tariff'


    # promocodes states (эти состояния не задейственны)
    state_promo_my = "state_promo_my"
    state_promo_create = "state_promo_create"
    state_promo_name = "state_promo_name"


class GetuserInfo(StatesGroup):
        twitter = State()
        get_username = State()
        address = State()
        text = State()
        next_stage = State()
        get_img = State()
        get_keyboard = State()
        finishpost = State()
        publish = State()
        reason = State()
        discord = State()


class Statistic(StatesGroup):
    date = State()
    next_stage = State()

