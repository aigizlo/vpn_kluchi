import urllib3
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from outline_api import (

    Manager)

#проверка на подписку в канал (на сервере)
# tg_channel = "@corbots"
# tg_channel_link = 'https://t.me/corbots'



# проверка на подписку в канал (на сервере)
tg_channel = "@off_radar"
tg_channel_link = 'https://t.me/off_radar'


# локально
bot_name = 'vpn_offradar_bot'
token = '6820291522:AAHbWTF-zSlL3bIdDqmjqSajYBsGbueRlQs'

# на сервере
# bot_name = 'vpnklyuchi_bot'
# token = '6509663632:AAGG38zVCvSe89tb46ZlhhQiZx53ADABHIQ'

support = "@off_radar_support"

admin = 502811372

# aiogram
bot = Bot(token=token)


storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

# Указываем Merchant ID и Secret Key от AnyPay
merchant_id = '156CC3CBD6B66EFF7F'
secret_key = 'JtoNDvlTxrQamCDSIDqgWU4DFzSpSTUihoFPMEs'
project_id = '13544'

# # Указываем Merchant ID и Secret Key от Free_kassa
#
# secret_word1 = 'DP.oy$a]CsVB=)B'
# secret_word2 = '$w$79)98%^u9}tj'
# free_kassa_merchant_id = '40657'


# fropay
secret_key_fropay = '0grmf2jskih1v4x'
public_key_fropay = 'f49otphlr7e06jg'
shop_id_fropay = '3904'




# данные для подлкючения к бд в локалке
host = "localhost"
user = "aigiz"
password = "Imaroot1"
database = "outline"

# данные для подлкючения к бд на сервере
# host = "localhost"
# user = "admin"
# password = "outline_admin"
# database = "outline"



# данные для подключения к менеджеру outline
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# apiurl_amsterdam = "https://212.118.53.231:40863/tUVEBiy0F8Qm8zyC8VXrjg"
# apicrt_amsterdam = "744393954-c8cc-4d71-bbc0-378914440ed3"

# сервер номер 1 Germany
apiurl_germany = "https://79.137.207.134:9250/F428WH0fsYzU8XDTiIa7eg"
apicrt_germany = "8bbcaf2e-41e9-4cd0-925b-f72fc3a2d556"

# сервер номер 2 usa
apiurl_usa = 'https://178.236.247.234:17797/-3zLKta0A-9p8h7rz0DnoA'
apicrt_usa = '6f886399-ab59-4eac-9cdf-626f4839ea8e'

# apiurl_kz = "https://188.225.31.86:3768/23V3Fbs0ttuPiYWf1TCq5A"
# apicrt_kz = "da6896f9-4f3e-47d5-b8b5-b4cec9aaf3cd"

# apiurl_spb = "https://45.153.69.147:23454/a4PAg9Ydh7yCSXTO5yBG6g"
# apicrt_spb = "e540ff22-ace2-4d5a-8810-8786a34d38b0"

# apiurl_turkey = "https://185.219.134.225:1719/FyENbYMQxz_W9UTK_sEnzA"
# apicrt_turkey = "83e234a9-7b7e-4f95-b6de-7f0022e89de8"


# manager_amsterdam = Manager(apiurl=apiurl_amsterdam, apicrt=apicrt_amsterdam)

manager_germany = Manager(apiurl=apiurl_germany, apicrt=apicrt_germany)
#
# manager_kz = Manager(apiurl=apiurl_kz, apicrt=apicrt_kz)
#
# manager_spb = Manager(apiurl=apiurl_spb, apicrt=apicrt_spb)
#
# manager_turkey = Manager(apiurl=apiurl_turkey, apicrt=apicrt_turkey)

manager_usa = Manager(apiurl=apiurl_usa, apicrt=apicrt_usa)

managers = {
    1: manager_germany,
    2: manager_usa,
}




# коэфициент реферального бонуса
coefficeint_bonus = 0.2


# для партнеров реферальный бонус 50%
partners = [1]
partner_bonus = 0.5
# имеют доступ к админским командам
admin_from_config = [502811372, 1139164093, 235013345]
# уведомления об ошибках
err_send = 502811372


# цены
one_month = 149
three_month = 299
one_year = 1199
article = 'https://telegra.ph/Kak-rabotaet-servis-Outline-Nadezhnost-i-Ustojchivost-k-Blokirovkam-10-03'


# file_ids = {'video': 'BAACAgIAAxkBAAIC7mWtQBk2CFTOC96pV0ihzwsZO0COAAJISwACV9doSf-4Rhw2Xu7-NAQ',
#             'menu': 'AgACAgIAAxkBAAIC72WtQBtufv9SxI86dqguU0beA0q4AAIh1TEbV9doSdd55L9lB5rrAQADAgADeAADNAQ',
#             'my_keys': 'AgACAgIAAxkBAAIC8GWtQCXMh-NsyXhShIAjnApXUcgLAAIi1TEbV9doSTHjXpNLkyBJAQADAgADeAADNAQ',
#             'bill': 'AgACAgIAAxkBAAIC8mWtQDyqSDLJSbCary2t2Mlljkr5AAIj1TEbV9doSW6115_lZaAwAQADAgADeAADNAQ',
#             'logger.info': 'AgACAgIAAxkBAAIC82WtQFp71VcQXnWjn22Q9UFu7ZQnAAIk1TEbV9doSUKqlXowHDcxAQADAgADeAADNAQ',
#             'change_location': 'AgACAgIAAxkBAAIC9GWtQIo2AabFua74D-60hkB1iYeNAAIk1TEbV9doSUKqlXowHDcxAQADAgADeAADNAQ',
#             'key_delete': 'AgACAgIAAxkBAAIC9WWtQJbunXm3dfXGgQf6qQdNEAJBAAIl1TEbV9doSTvT0QluqlIhAQADAgADeAADNAQ',
#             'key': 'AgACAgIAAxkBAAIC9mWtQKUR60VaYTw2OYoJf0SSLu0EAAIm1TEbV9doSYkVOhkxDRVbAQADAgADeAADNAQ',
#             'location': 'AgACAgIAAxkBAAIC92WtQKoAAR5017N1Yb4VnZBCHsT5TwACJ9UxG1fXaEkXARFIHx71jwEAAwIAA3gAAzQE',
#             'present': 'AgACAgIAAxkBAAIC-GWtQLXHmR8UwHIBM2ylcDCz6BMIAAIo1TEbV9doSRZ3gmVl70rEAQADAgADeAADNAQ',
#             'renewal_ok': 'AgACAgIAAxkBAAIC-WWtQM26KyXm6JBSYY3sk-Tjs15FAAIp1TEbV9doSeuEltvYO7nDAQADAgADeAADNAQ',
#             'renewal': 'AgACAgIAAxkBAAIC-mWtQNhVUC-6xm8t3bzvrvkrBIiCAAIq1TEbV9doST_iocBMc2luAQADAgADeAADNAQ',
#             'tarrif': 'AgACAgIAAxkBAAIC-2WtQOSUXZsTNtTKufRdGJTqJN1HAAIr1TEbV9doSYMbEV95cytrAQADAgADeAADNAQ',
#             'why_we': 'AgACAgIAAxkBAAIC_GWtQO1yksOEy9R7yAsn9s6koYF6AAIt1TEbV9doSekBbT0s9aunAQADAgADeAADNAQ'}

file_ids = {'video': 'BAACAgIAAxkBAAITi2Ww2MOAcbsbFgSnNfcQOgGEthLoAALCSAACxXqJSY5zno9hOGT_NAQ',
            'menu': 'AgACAgIAAxkBAAITiWWw2E6havYW35TyNbMu7_CZa6_OAALq1zEbxXqJSdzu98LIMBzJAQADAgADeAADNAQ',
            'my_keys': 'AgACAgIAAxkBAAITimWw2IBfhJsz1fGmX9YQnP_1Vs3YAALz1zEbxXqJSbtJH7dYopJpAQADAgADeAADNAQ',
            'bill': 'AgACAgIAAxkBAAITjGWw2M9yVDfZO2rg-ygg_InHKxTRAAL01zEbxXqJSWKvBTD6L_oAAQEAAwIAA3gAAzQE',
            'change_location': 'AgACAgIAAxkBAAITjWWw2PQoj0bwpUAE9_9xV_A8EEXAAAL11zEbxXqJSWnKL0-trCcgAQADAgADeAADNAQ',
            'key_delete': 'AgACAgIAAxkBAAITjmWw2RB5j0rlerKHge_cgH3ACb7LAAL21zEbxXqJSa3LSgOi1iGXAQADAgADeAADNAQ',
            'key': 'AgACAgIAAxkBAAITj2Ww2SL7gDMvVWnHsXyuNlvzdUihAAL21zEbxXqJSa3LSgOi1iGXAQADAgADeAADNAQ',
            'location': 'AgACAgIAAxkBAAITkGWw2TPq5MbcQWZigqHBwx7qmvRTAAL31zEbxXqJSWcX-At_HCihAQADAgADeAADNAQ',
            'present': 'AgACAgIAAxkBAAITkWWw2UDrt06FW8azlWSx1csdUlpPAAL41zEbxXqJSV01Xv4AASFKEgEAAwIAA3gAAzQE',
            'renewal_ok': 'AgACAgIAAxkBAAITkmWw2UziQ5mNkfzBnhDBdh4g_KXqAAL51zEbxXqJSXLaBntnUrWuAQADAgADeAADNAQ',
            'renewal': 'AgACAgIAAxkBAAITk2Ww2Vg2Tw_nRuwXClx2T5myUgZ0AAL61zEbxXqJSYMl9z5ZIGCvAQADAgADeAADNAQ',
            'tarrif': 'AgACAgIAAxkBAAITlGWw2WSgFYKHokp0FlYFDG9jt-VLAAL71zEbxXqJSYvsuBhM3htZAQADAgADeAADNAQ',
            'why_we': 'AgACAgIAAxkBAAITlWWw2XPAFSLAA1x-7bPHx8nm3503AAL81zEbxXqJSY6bDycVxxz1AQADAgADeAADNAQ'}


