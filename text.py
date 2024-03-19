from config import support

why_we = """🚀 Быстрый VPN без ограничений

✅ Быстрое поключение к VPN без рекламы 

🌎 VPN доступен, из любой точки мира, где есть интернет

🛡 Приватный VPN не блокируется в отличие от публичных сервисов

😎 Смешанный трафик труднее блокировать, обнаружить и отследить

👉 <a href="https://telegra.ph/Kak-rabotaet-servis-Nadezhnost-i-Ustojchivost-k-Blokirovkam-01-19">Больше информации читайте в статье</a>"""

server_id_country = {
    1: '🇩🇪Германия Франкфурт',
    2: '🇺🇸Америка Лос Анджелес'
}


def ref_link(user_id, bot_name, count, balance):
    text = f"🤝 Приглашайте друзей по своей реферальной ссылке и получайте 20%" \
           f"от каждой их покупки и продления ключа\n\n" \
           f"💰Это реальная возможность создать свой пассивный доход! \n\n" \
           f'💳 Выводите деньги на карту или покупайте ключи\n\n' \
           f"Ваш ID : {user_id}\n" \
           f"Вы пригласили: {count} человек\n" \
           f"Ваш партнерский баланс: {balance} рублей\n\n" \
           f"Ваша реферальная ссылка : <code>https://t.me/{bot_name}?start={user_id}</code>\n\n"
    return text


menu_txt = """🌏 Как пользоваться VPN?

✅ Шаг 1: Скачайте приложение Outline на Android, iPhone, Windows, MacOS

✅ Шаг 2: Получите ключ и вставьте его в скаченное приложении

✅ Шаг 3: Готово! Теперь у вас стабильный VPN без рекламы

Подключайтесь за 2 секунды! 👍"""

not_bot_text = "Что бы пользоваться телеграм-ботом, пожалуйста, подтвердите, что вы не робот. Нажмите на «Я не робот»"


def answer_if_change(location):
    global instruction
    answer = f"""Локация ключа изменена! 👌

📍Локация: {location}    
{instruction}
<b>НИЖЕ ВАШ КЛЮЧ 🔑</b>
👇 (кликни для копирования)
"""
    return answer


answer_not_keys = """😔 У вас еще нет ключей!
                
✅ Чтобы приобрести ключ, нажмите "Получить ключ" """

instruction = """
<b>🌏 Как пользоваться VPN?</b>

<b>✅Шаг 1:</b> Скачайте приложение Outline <a href="https://play.google.com/store/apps/details?id=org.outline.android.client">Android</a>, <a href="https://apps.apple.com/us/app/outline-app/id1356177741">iPhone</a>, <a href="https://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe">Windows</a>, <a href="https://apps.apple.com/us/app/outline-app/id1356178125">MacOS</a>

<b>✅Шаг 2:</b> Получите ключ и вставьте его в скаченное приложении

<b>✅Шаг 3:</b> Готово! Теперь у вас стабильный VPN без рекламы

Подключайтесь за 2 секунды! 👍
"""

instruction2 = """
<b>🌏 Как пользоваться VPN?</b>
<b>✅Шаг 1:</b> Скачайте приложение Outline <a href="https://play.google.com/store/apps/details?id=org.outline.android.client">Android</a>, <a href="https://apps.apple.com/us/app/outline-app/id1356177741">iPhone</a>, <a href="https://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe">Windows</a>, <a href="https://apps.apple.com/us/app/outline-app/id1356178125">MacOS</a>
<b>✅Шаг 2:</b> Получите ключ и вставьте его в скаченное приложении
<b>✅Шаг 3:</b> Готово! Теперь у вас стабильный VPN без рекламы
"""

promotion_text = """10 дней в подарок🎁"""

answer_error = f"Произошла ошибка!\n" \
               f"Пожалуйста, попробуйте снова или обратитесь в службу поддержки {support}"


def payment_amount_prompt(amount):
    text = f"Сумма покупки {amount} рублей, выберите способ оплаты:"

    return text


subscription_prompt = "Выберите, на сколько месяцев оформить подписку"


# ответы об оплате
def answer_if_buy(server_id):
    global instruction
    location = server_id_country.get(server_id)

    answer_if_buy = f"""Покупка прошла успешно👌!
    
📍Локация: {location}  
{instruction}

<b>НИЖЕ ВАШ КЛЮЧ 🔑</b>
👇 (кликни для копирования)
"""
    return answer_if_buy


answer_if_not_balance = "😔 Недостаточно средств на партнерском счете\n" \
                        "👇 Выберите платежную систему для оплаты"


def text_free_tariff(server_id):
    location = server_id_country.get(server_id)

    txt = f"<b>Вы получили подарок! 🎁</b>\n" \
          f"📍Локация: {location}\n\n" \
          f"{instruction2}\n\n" \
          f"<b>НИЖЕ ВАШ КЛЮЧ 🔑</b>\n" \
          f"👇 (кликни для копирования)"

    return txt
