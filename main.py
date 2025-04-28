import os
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

bot_mode = 'off'
waiting_for_confirmation = False

def send_telegram_message(message):
    pass  # Aqui seria a função de envio para o Telegram

def log_event(message):
    print(message)

@app.route('/', methods=['POST'])
def telegram_webhook():
    global bot_mode, waiting_for_confirmation
    data = request.get_json()
    if 'message' in data:
        text = data['message']['text']
        if text == '/modo_auto':
            bot_mode = 'auto'
            send_telegram_message("✅ Modo AUTOMÁTICO ativado!")
            log_event("Modo AUTOMÁTICO ativado")
        elif text == '/modo_semi':
            bot_mode = 'semi'
            send_telegram_message("✅ Modo SEMI-AUTOMÁTICO ativado!")
            log_event("Modo SEMI-AUTOMÁTICO ativado")
        elif text == '/parar':
            bot_mode = 'off'
            send_telegram_message("🛑 Bot parado!")
            log_event("Bot parado!")
    return jsonify({"ok": True})

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))).start()