import os
import threading
from flask import Flask, request

app = Flask(__name__)

bot_mode = "auto"
waiting_for_confirmation = False

@app.route(f"/{os.environ['TELEGRAM_TOKEN']}", methods=["POST"])
def telegram_webhook():
    data = request.json
    if 'message' in data:
        text = data['message'].get('text', '')
        global bot_mode, waiting_for_confirmation
        if text == '/modo_auto':
            bot_mode = 'auto'
        elif text == '/modo_semi':
            bot_mode = 'semi'
        elif text == '/parar':
            bot_mode = 'off'
    elif 'callback_query' in data:
        callback_data = data['callback_query']['data']
        if callback_data == 'confirm_entry' and waiting_for_confirmation:
            waiting_for_confirmation = False
        elif callback_data == 'cancel_entry':
            waiting_for_confirmation = False
    return 'ok'

def bot_loop():
    while True:
        pass  # Aqui ficaria sua lógica de operação

if __name__ == "__main__":
    threading.Thread(target=bot_loop).start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
