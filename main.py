import os
import time
import requests
import pandas as pd
import telebot
from flask import Flask, request
import threading

# Configurações iniciais
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

symbols = [
    '1000PEPEUSDT', 'WLDUSDT', 'RNDRUSDT', 'TNSRUSDT', 'BOMEUSDT', 'ENAUSDT', 'MNTUSDT', 'TNSRUSDT',
    'WIFUSDT', 'PYTHUSDT', 'GRTUSDT', 'MAVIAUSDT', 'IDUSDT', 'SAGAUSDT', 'ONDOUSDT', 'SUIUSDT',
    'XAIUSDT', 'STRKUSDT', 'ARUSDT', 'JUPUSDT', 'ACEUSDT', 'METISUSDT', 'FETUSDT', 'PENDLEUSDT',
    'LQTYUSDT', 'HIFIUSDT', 'AIDOGEUSDT', 'NTRNUSDT', 'TNSRUSDT', 'MANTAUSDT', 'ALTUSDT', 'TAOUSDT',
    'PORTALUSDT', 'LUNAUSDT', 'OMNIUSDT', 'FLOKIUSDT', 'GALAUSDT', 'IMXUSDT', 'RDNTUSDT', 'DOGEUSDT',
    'COTIUSDT', 'AKTUSDT', 'GALUSDT', 'BLURUSDT', 'RNDRUSDT', 'MAGICUSDT', 'CANTOUSDT', 'DYDXUSDT',
    'KASUSDT', 'BIGTIMEUSDT'
]

intervalos = ['5m', '15m']

def buscar_candles(symbol, interval, limit=50):
    url = f'https://api.mexc.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    try:
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Erro ao buscar candles de {symbol}: {e}")
        return None

def calcular_rsi(df, period=14):
    delta = df[4].astype(float).diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def verificar_sinais():
    while True:
        for symbol in symbols:
            for intervalo in intervalos:
                df = buscar_candles(symbol, intervalo)
                if df is None or len(df) < 20:
                    continue

                rsi = calcular_rsi(df)
                if rsi.iloc[-1] <= 30:
                    enviar_alerta(f"🟢 SINAL DE COMPRA ({intervalo}) - {symbol} - RSI: {rsi.iloc[-1]:.2f}")
                elif rsi.iloc[-1] >= 70:
                    enviar_alerta(f"🔴 SINAL DE VENDA ({intervalo}) - {symbol} - RSI: {rsi.iloc[-1]:.2f}")

        time.sleep(300)  # Espera 5 minutos

def enviar_alerta(mensagem):
    print(mensagem)
    try:
        bot.send_message(chat_id="@SeuCanalOuChatID", text=mensagem)
    except Exception as e:
        print(f"Erro ao enviar alerta no Telegram: {e}")

# Botões do Bot
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ Bot iniciado! Analisando altcoins...")

@bot.message_handler(commands=['status'])
def status(message):
    bot.send_message(message.chat.id, "✅ Bot está ativo e rodando!")

@bot.message_handler(commands=['parar'])
def parar(message):
    bot.send_message(message.chat.id, "🛑 Parando bot (não implementado ainda via comando)")

# Webhook para Railway
@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'ok', 200

# Inicialização
def iniciar_bot():
    threading.Thread(target=verificar_sinais).start()

if __name__ == '__main__':
    iniciar_bot()
    app.run(host="0.0.0.0", port=8080)
