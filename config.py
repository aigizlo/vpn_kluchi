import urllib3
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from outline_api import (

    Manager)

# Настройки бота
# token = '6074035686:AAEWCJFAsnRdOBBRNNtl56Ef-wed8m-ucZg'
#
# bot_name = 'outlinexbot'
#
#
token = '6353790329:AAHQYdMTQ9mSuPkdw80DuOlerpsuhOq0qzo'

bot_name = 'off_radar_bot'

support = "@outlinex_support"

bot = Bot(token=token)

storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)

# Указываем Merchant ID и Secret Key от AnyPay
merchant_id = '156CC3CBD6B66EFF7F'
secret_key = '5gu8fRE3dxWUzuIsrKCa3iV2e5UfvSe1T3tT7MO'
project_id = '12622'


# данные для подлкючения к бд
host = "localhost"
user = "aigiz"
password = "Imaroot1"
database = "outline"

# данные для подключения к менеджеру outline
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# cервер номер 1 Nederland
apiurl_amsterdam = "https://212.118.53.231:40863/tUVEBiy0F8Qm8zyC8VXrjg"
apicrt_amsterdam = "744393954-c8cc-4d71-bbc0-378914440ed3"

# сервер номер 2 Germany
apiurl_germany = "https://89.208.103.199:3509/SmiTzdKTj715pmUI-2mCbg"
apicrt_germany = "adb4d844-ccf5-4a47-a2aa-008091a544fe"

# сервер номер 3 Kazahstan
apiurl_kz = "https://188.225.31.86:3768/23V3Fbs0ttuPiYWf1TCq5A"
apicrt_kz = "da6896f9-4f3e-47d5-b8b5-b4cec9aaf3cd"

# сервер номер 4 Sankt-Pirerburg
apiurl_spb = "https://45.153.69.147:23454/a4PAg9Ydh7yCSXTO5yBG6g"
apicrt_spb = "e540ff22-ace2-4d5a-8810-8786a34d38b0"

# сервер номер 5 Turkey
apiurl_turkey = "https://185.219.134.225:1719/FyENbYMQxz_W9UTK_sEnzA"
apicrt_turkey = "83e234a9-7b7e-4f95-b6de-7f0022e89de8"

manager_amsterdam = Manager(apiurl=apiurl_amsterdam, apicrt=apicrt_amsterdam)

manager_germany = Manager(apiurl=apiurl_germany, apicrt=apicrt_germany)

manager_kz = Manager(apiurl=apiurl_kz, apicrt=apicrt_kz)

manager_spb = Manager(apiurl=apiurl_spb, apicrt=apicrt_spb)

manager_turkey = Manager(apiurl=apiurl_turkey, apicrt=apicrt_turkey)

managers = {
    1: manager_amsterdam,
    2: manager_germany,
    3: manager_kz,
    4: manager_spb,
    5: manager_turkey
}
# коэфициент реферального бонуса
coefficeint_bonus = 0.2
# имеют доступ к админским командам
admin_from_config = [502811372, 1139164093, 235013345]
# уведомления об ошибках
err_send = 502811372


# цены
one_month = 149
two_month = 269
three_month = 405
six_month = 810


# api_wallet = "boPvJGD9zMPvFUqVltLpe96sFF5lcd8pciC3"