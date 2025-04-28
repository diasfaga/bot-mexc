import os
import threading
from flask import Flask, request
import requests

app = Flask(__name__)

bot_mode = "off"
waiting_for_confirmation = False
latest_signal = None

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
telegram_token = os.getenv('TELEGRAM_TOKEN')
telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    payload = {
        "chat_id": telegram_chat_id,
        "text": text
    }
    requests.post(url, json=payload)

@app.route(f"/{telegram_token}", methods=["POST"])
def telegram_webhook():
    global bot_mode, waiting_for_confirmation
    data = request.get_json()
    if 'message' in data:
        text = data['message']['text']
        if text == '/modo_auto':
            bot_mode = 'auto'
            send_telegram_message('✅ Bot em modo AUTOMÁTICO!')
        elif text == '/modo_semi':
            bot_mode = 'semi'
            send_telegram_message('✅ Bot em modo SEMI-AUTOMÁTICO!')
        elif text == '/parar':
            bot_mode = 'off'
            send_telegram_message('🛑 Bot PARADO!')
    return 'ok'

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": port}).start()