import urllib3
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from outline_api import (

    Manager)

#проверка на подписку в канал (на сервере)
tg_channel = "@corbots"


# проверка на подписку в канал (на сервере)
# tg_channel = "@off_radar"
# локально
# bot_name = 'vpn_offradar_bot'
# token = '6820291522:AAHbWTF-zSlL3bIdDqmjqSajYBsGbueRlQs'

# на сервере
bot_name = 'vpnklyuchi_bot'
token = '6509663632:AAGG38zVCvSe89tb46ZlhhQiZx53ADABHIQ'

support = "@off_radar_support"

admin = 502811372

# aiogram
bot = Bot(token=token)


storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

# Указываем Merchant ID и Secret Key от AnyPay
merchant_id = '156CC3CBD6B66EFF7F'
secret_key = '5gu8fRE3dxWUzuIsrKCa3iV2e5UfvSe1T3tT7MO'
project_id = '12622'

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
# host = "localhost"
# user = "aigiz"
# password = "Imaroot1"
# database = "outline"

# данные для подлкючения к бд на сервере
host = "localhost"
user = "admin"
password = "outline_admin"
database = "outline"



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
one_year = 1499

