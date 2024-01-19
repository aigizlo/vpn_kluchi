from config import support

why_we = """🚀 Быстрый VPN без ограничений

✅ Быстрое поключение к VPN без рекламы 

🌎 VPN доступен, из любой точки мира, где есть интернет

🛡 Приватный VPN не блокируется в отличие от публичных сервисов

😎 Смешанный трафик труднее блокировать, обнаружить и отследить

👉 <a href="https://telegra.ph/Kak-rabotaet-servis-Nadezhnost-i-Ustojchivost-k-Blokirovkam-01-19">Больше информации читайте в статье</a>"""

server_id_country = {
    1: '🇱🇺Нидерланды Амстердам',
    2: '🇩🇪Германия Франкфурт',
    3: '🇰🇿Казахстан Астана',
    4: '🇷🇺Россия',
    5: '🇹🇷Турция Стамбул',
    6: '🇺🇸Америка Лос Анджелес'
}

menu_txt = """🌏 Как пользоваться VPN?

✅ Шаг 1: Скачайте приложение на Android, iPhone, Windows, MacOS

✅ Шаг 2: Получите ключ и вставьте его в скаченное приложении

✅ Шаг 3: Готово! Теперь у вас стабильный VPN без рекламы

Подключайтесь за 2 секунды! 👍"""

not_bot_text = "Что бы пользоваться телеграм-ботом, пожалуйста, подтвердите, что вы не робот. Нажмите на «Я не робот»"


def answer_if_change(key_value, location):
    global instruction
    answer = f"""Локация ключа изменена! 👌

📍Локация: {location}    

<b>ВАШ КЛЮЧ 🔑</b>
👇 (кликни для копирования)
<code>{key_value}</code>
"""
    return answer + instruction


answer_not_keys = """😔 У вас еще нет ключей!
                
✅ Чтобы приобрести ключ, нажмите "Получить ключ" """

instruction = """
<b>🌏 Как пользоваться VPN?</b>

<b>✅Шаг 1:</b> Скачайте приложение <a href="https://play.google.com/store/apps/details?id=org.outline.android.client">Android</a>, <a href="https://apps.apple.com/us/app/outline-app/id1356177741">iPhone</a>, <a href="https://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe">Windows</a>, <a href="https://apps.apple.com/us/app/outline-app/id1356178125">MacOS</a>

<b>✅Шаг 2:</b> Получите ключ и вставьте его в скаченное приложении

<b>✅Шаг 3:</b> Готово! Теперь у вас стабильный VPN без рекламы

Подключайтесь за 2 секунды! 👍
"""

instruction2 = """
<b>🌏 Как пользоваться VPN?</b>
<b>✅Шаг 1:</b> Скачайте приложение <a href="https://play.google.com/store/apps/details?id=org.outline.android.client">Android</a>, <a href="https://apps.apple.com/us/app/outline-app/id1356177741">iPhone</a>, <a href="https://s3.amazonaws.com/outline-releases/client/windows/stable/Outline-Client.exe">Windows</a>, <a href="https://apps.apple.com/us/app/outline-app/id1356178125">MacOS</a>
<b>✅Шаг 2:</b> Получите ключ и вставьте его в скаченное приложении
<b>✅Шаг 3:</b> Готово! Теперь у вас стабильный VPN без рекламы
"""

promotion_text = """3 дня в подарок🎁"""

answer_error = f"Произошла ошибка!\n" \
               f"Пожалуйста, попробуйте снова или обратитесь в службу поддержки {support}"


def payment_amount_prompt(amount):
    text = f"Сумма покупки {amount} рублей, выберите способ оплаты:"

    return text


subscription_prompt = "Выберите, на сколько месяцев оформить подписку"


# ответы об оплате
def answer_if_buy(key_value, server_id):
    global instruction2
    location = server_id_country.get(server_id)

    answer_if_buy = f"""Покупка прошла успешно👌!
    
📍Локация: {location}    

<b>ВАШ КЛЮЧ 🔑</b>
👇 (кликни для копирования)
<code>{key_value}</code>
"""
    return answer_if_buy + instruction2


answer_if_not_balance = "Недостаточно средств. Пожалуйста, пополните ваш баланс.\n" \
                        "👇Выберите необходимую сумму для оплаты👇"

def text_free_tariff(server_id, key_value):
    location = server_id_country.get(server_id)

    txt = f"<b>Вы получили подарок! 🎁</b>\n\n" \
          f"📍Локация: {location}\n\n" \
          f"<b>ВАШ КЛЮЧ 🔑</b>\n" \
          f"<b>👇(Кликните для копирования)</b>\n" \
          f"– <code>{key_value}</code>\n\n" \

    return txt + instruction2
