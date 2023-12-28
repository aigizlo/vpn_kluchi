from user_data import execute_query
from logger import logger
from telebot_ import free_tariff_telebot_kb, sync_send_message, get_key_kb

#
# txt_if_use_trail = """Стандартные VPN легко обнаружить и заблокировать.
#
# Система Outline не подведет, когда другие VPN откажут: наш сервис невозможно отследить и заблокировать на основе сетей или IP-адресов.
#
# Прочитайте <a href="https://telegra.ph/Kak-rabotaet-servis-Outline-Nadezhnost-i-Ustojchivost-k-Blokirovkam-10-03">статью о преимуществах Outline</a> и почему даже Китайский фаервол тут бессилен - <a href="https://telegra.ph/Kak-rabotaet-servis-Outline-Nadezhnost-i-Ustojchivost-k-Blokirovkam-10-03">читать статью</a>
#
# Если вы все еще не попробовали 👇👇👇"""
#
# txt_if_not_use_trail = """Стандартные VPN легко обнаружить и заблокировать.
#
# Система Outline не подведет, когда другие VPN откажут: наш сервис невозможно отследить и заблокировать на основе сетей или IP-адресов.
#
# Прочитайте <a href="https://telegra.ph/Kak-rabotaet-servis-Outline-Nadezhnost-i-Ustojchivost-k-Blokirovkam-10-03">статью о преимуществах Outline</a> и почему даже Китайский фаервол тут бессилен - <a href="https://telegra.ph/Kak-rabotaet-servis-Outline-Nadezhnost-i-Ustojchivost-k-Blokirovkam-10-03">читать статью</a>
# """


txt_promo = """<b>🎁Акция - Месяц в подарок!🎁" </b>

<b>Внимание, ценители безопасности и конфиденциальности! 🌐</b>

Только одна неделя, чтобы взлететь в небеса анонимности с <b>Off Radar VPN</b>! 🚀

Приобретайте или продлевайте свой VPN на любой срок, и мы подарим вам <b>целый месяц дополнительно!</b> 🎁

Это уникальная возможность обеспечить себе <b>надежную защиту и анонимность</b> в онлайне на долгие месяцы вперед! 🔒

Не упустите этот шанс! Акция длится всего неделю, так что <b>действуйте прямо сейчас!</b> 💼

Подключайтесь к <b>Off Radar VPN</b> и оставайтесь вне зоны видимости в онлайне! 💻✨

Жми -> "🔐Получить ключ"👇
"""
def get_users_not_use_trial():

    sql = "SELECT telegram_id FROM users WHERE message = 1 and free_tariff = 0"
    sql2 = 'SELECT telegram_id FROM users WHERE message = 1 and free_tariff IN (1, 2)'
    sql_update_message = 'UPDATE users SET message = 0'

    # получаем id всех кто не использовал триал, и кому не отправлялась промо сообщение
    result = execute_query(sql)
    # получаем id всех кто использовал триал или отказался, и кому не отправлялась промо сообщение
    result2 = execute_query(sql2)
    # отмечаем всех, кому сообщение отправилось
    execute_query(sql_update_message)

    list_telegram_id = []
    list_telegram_id_2 = []

    for tg in result:
        list_telegram_id.append(tg[0])

    for tg in result2:
        list_telegram_id_2.append(tg[0])

    return list_telegram_id, list_telegram_id_2


def sender_promo_txt():
    lst_tgs, lst_tgs2 = get_users_not_use_trial()
    count = 0
    count2 = 0
    if lst_tgs != []:
        for tg in lst_tgs:
            try:
                sync_send_message(tg, txt_promo, "HTML")
                count += 1
            except Exception as e:
                count2 += 1
                logger.error(f"{tg} - добавил в чс")
    if lst_tgs2 != []:
        for tg in lst_tgs2:
            try:
                sync_send_message(tg, txt_promo, "HTML")
                count += 1
            except Exception as e:
                count2 += 1
                logger.error(f"{tg} - добавил в чс")
    if count:
        logger.info(f'Промо текс отправлен {count} юзерам , Не доставлено  - {count2}')


def searche_key_id_user_id(pay_id):
    sql = """select key_id, user_id from bills where pay_id = %s"""

    result = execute_query(sql, (pay_id,))

    return result[0]

# print(searche_key_id_user_id(102))