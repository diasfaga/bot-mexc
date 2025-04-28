from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Pegando o token do Telegram pelas variáveis de ambiente
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# URL da API do Telegram
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Rota para o Webhook (importante usar apenas /<token>)
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Bot iniciado! ✅")
        elif text == "/status":
            send_message(chat_id, "Bot está rodando! 🚀")
        else:
            send_message(chat_id, "Comando não reconhecido. 🤖")

    return {"ok": True}

def send_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
