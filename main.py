import os
import requests
import pandas as pd
import time
from flask import Flask, request

# Configurações
API_URL = "https://api.mexc.com"
TOKEN = os.getenv('TELEGRAM_TOKEN')  # Variável do Railway
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')  # Adicionar se quiser travar para um chat específico

# Parâmetros de análise
symbols = []  # Aqui vamos carregar as 50 melhores altcoins depois
intervals = ["5m", "15m"]  # 5 minutos e 15 minutos
rsi_period = 14
check_frequency_seconds = 300  # 5 minutos

# Iniciar app Flask
app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"].lower()

        if text == "/start":
            send_message(chat_id, "✅ Bot iniciado com sucesso!")
        elif text == "/status":
            send_message(chat_id, "✅ Bot está ativo!")
        else:
            send_message(chat_id, "❓ Comando não reconhecido.")
    
    return "ok"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    requests.post(url, json=payload)

def get_klines(symbol, interval, limit=100):
    url = f"{API_URL}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base', 'taker_buy_quote', 'ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def check_signals():
    print("🔍 Verificando sinais...")
    for symbol in symbols:
        for interval in intervals:
            try:
                df = get_klines(symbol, interval)
                df['RSI'] = calculate_rsi(df)

                last_rsi = df['RSI'].iloc[-1]
                last_close = df['close'].iloc[-1]
                previous_close = df['close'].iloc[-2]

                message = None

                # Sinal RSI
                if last_rsi < 30:
                    message = f"🔵 [M{interval}] {symbol}: RSI {last_rsi:.2f} ➔ Possível COMPRA!"
                elif last_rsi > 70:
                    message = f"🔴 [M{interval}] {symbol}: RSI {last_rsi:.2f} ➔ Possível VENDA!"

                # Rompimento simples
                if last_close > df['high'].iloc[-2]:
                    message = f"🚀 [M{interval}] {symbol}: Rompimento pra CIMA detectado!"
                elif last_close < df['low'].iloc[-2]:
                    message = f"⚡ [M{interval}] {symbol}: Rompimento pra BAIXO detectado!"

                if message:
                    send_message(CHAT_ID, message)
                    print(message)
                    
            except Exception as e:
                print(f"Erro ao analisar {symbol}: {e}")

def load_symbols():
    print("🔄 Carregando as 50 melhores altcoins...")
    global symbols
    url = f"{API_URL}/api/v3/exchangeInfo"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        all_symbols = [s['symbol'] for s in data['symbols'] if s['quoteAsset'] == 'USDT']
        # Remove BTC, ETH, BNB, SOL
        filtered = [s for s in all_symbols if not any(x in s for x in ["BTC", "ETH", "BNB", "SOL"])]
        symbols = filtered[:50]
        print(f"✅ {len(symbols)} altcoins carregadas.")
    else:
        print("Erro ao carregar símbolos da MEXC")

if __name__ == "__main__":
    load_symbols()
    send_message(CHAT_ID, "🚀 Bot de sinais iniciado!")
    while True:
        check_signals()
        time.sleep(check_frequency_seconds)
