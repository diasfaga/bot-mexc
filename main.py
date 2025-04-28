from flask import Flask, request, send_file
import requests
import pandas as pd
import time
import os
import threading
from datetime import datetime

# Telegram Configurações
BOT_TOKEN = '7787547636:AAH58KZPuNb90FWVGx3EQQsCpvrMQieMq3s'
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
chat_id = None

# App Flask
app = Flask(__name__)

# Lista de moedas para monitorar
symbols = [
    'SAGAUSDT', 'ACEUSDT', 'PORTALUSDT', 'HIFIUSDT', 'ALTUSDT', 'ONIUSDT',
    'IMXUSDT', 'FLOKIUSDT', 'MAGICUSDT', 'DYDXUSDT', 'RNDRUSDT'
]

def send_message(text):
    if chat_id:
        url = f"{BASE_URL}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        requests.post(url, json=payload)

def send_planilha():
    if chat_id and os.path.exists('sinais.csv'):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
        with open('sinais.csv', 'rb') as file:
            files = {'document': file}
            data = {'chat_id': chat_id}
            requests.post(url, files=files, data=data)

def buscar_candles(symbol, interval, limit=100):
    url = f"https://api.mexc.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        if response.ok:
            df = pd.DataFrame(response.json())
            if df.shape[1] >= 6:
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'] + list(range(6, df.shape[1]))
                df['close'] = df['close'].astype(float)
                return df
        return None
    except Exception as e:
        print(f"Erro ao buscar candles de {symbol}: {e}")
        return None

def calcular_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def salvar_sinal(par, preco, tipo, rsi):
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = {'DataHora': data, 'Par': par, 'Tipo': tipo, 'Preço': preco, 'RSI': round(rsi, 2)}
    df = pd.DataFrame([linha])
    if os.path.exists('sinais.csv'):
        df.to_csv('sinais.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('sinais.csv', index=False)

def emitir_alerta_sonoro():
    try:
        import winsound
        winsound.Beep(1000, 500)
    except ImportError:
        print("🔔 Alerta (Beep) não suportado nesse servidor!")

def analisar_symbol(symbol):
    for timeframe in ['5m', '15m']:
        df = buscar_candles(symbol, timeframe)
        if df is not None and not df.empty:
            rsi = calcular_rsi(df).iloc[-1]
            preco = df['close'].iloc[-1]

            if rsi <= 30:
                mensagem = f"🟢 COMPRA: {symbol} [{timeframe}] | RSI: {rsi:.2f} | Preço: {preco}"
                send_message(mensagem)
                emitir_alerta_sonoro()
                salvar_sinal(symbol, preco, 'Compra', rsi)

            elif rsi >= 70:
                mensagem = f"🔴 VENDA: {symbol} [{timeframe}] | RSI: {rsi:.2f} | Preço: {preco}"
                send_message(mensagem)
                emitir_alerta_sonoro()
                salvar_sinal(symbol, preco, 'Venda', rsi)

def loop_sinais():
    while True:
        print('🔎 Analisando sinais...')
        for symbol in symbols:
            try:
                analisar_symbol(symbol)
            except Exception as e:
                print(f"Erro ao analisar {symbol}: {e}")
        time.sleep(300)  # 5 minutos

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    global chat_id
    update = request.get_json()

    if 'message' in update:
        chat_id = update['message']['chat']['id']
        texto = update['message'].get('text', '')

        if texto == '/start':
            send_message("✅ Bot iniciado! Monitorando Altcoins 🚀")
        elif texto == '/status':
            send_message("📊 Bot rodando normalmente! 🔥")
        elif texto == '/planilha':
            send_message("📄 Enviando a planilha de sinais...")
            send_planilha()

    return {'ok': True}

@app.route('/')
def home():
    return 'Bot de Sinais MEXC está online! 🚀'

if __name__ == '__main__':
    threading.Thread(target=loop_sinais).start()
    app.run(host="0.0.0.0", port=8080)
