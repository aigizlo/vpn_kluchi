from flask import Flask, request, jsonify
from config import bot, err_send
from aiogram.types import ParseMode
import json

app = Flask(__name__)


WEBHOOK_URL = "https://telegram.outlinevpn.space/notification"




@app.route('/notification', methods=['POST'])
def anypay_notification():
    # Получите данные уведомления от AnyPay
    data = request.json

    # Обработайте данные уведомления по вашим потребностям

    # Отправьте уведомление в Telegram
    message = f'Получено уведомление от AnyPay:\n{data}'
    print(message)

    return jsonify({'status': 'ok'})




