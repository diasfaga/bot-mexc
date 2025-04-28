from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    print(data)  # Para ver os dados recebidos do Telegram
    return '', 200

@app.route('/', methods=['GET'])
def index():
    return 'Bot está rodando!', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
