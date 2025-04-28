from flask import Flask, request
import requests

app = Flask(__name__)

# Seu token do bot Telegram
TOKEN = '7787547636:AAH58KZPuNb90FWVGx3EQQsCpvrMQieMq3s'
URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        if text == '/start':
            send_message(chat_id, '✅ Bot iniciado com sucesso!')
        elif text == '/status':
            send_message(chat_id, '✅ Bot está ativo!')
        else:
            send_message(chat_id, '🤖 Comando não reconhecido.')
            
    return '', 200

@app.route('/', methods=['GET'])
def index():
    return '🚀 Bot está online e funcionando!', 200

def send_message(chat_id, text):
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(URL, json=payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
