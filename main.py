from flask import Flask, request
import requests
import pandas as pd
import time

app = Flask(__name__)

BOT_TOKEN = '7787547636:AAH58KZPuNb90FWVGx3EQQsCpvrMQieMq3s'
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'
chat_id = None

symbols = [
    'SAGAUSDT', 'ACEUSDT', 'PORTALUSDT', 'HIFIUSDT', 'ALTUSDT', 'ONIUSDT',
    'IMXUSDT', 'FLOKIUSDT', 'MAGICUSDT', 'DYDXUSDT', 'RNDRUSDT'
]

def send_telegram_alert(message):
    global chat_id
    if chat_id:
        url = f'{BASE_URL}/sendMessage'
        payload = {'chat_id': chat_id, 'text': message}
        response = requests.post(url, json=payload)
        if not response.ok:
            print(f'Erro ao enviar alerta: {response.text}')
    else:
        print('chat_id ainda não registrado.')

def get_klines(symbol, interval, limit=100):
    url = f'https://api.mexc.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    response = requests.get(url)
    if response.ok:
        df = pd.DataFrame(response.json())
        if df.shape[1] >= 6:
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume'] + list(range(6, df.shape[1]))
            df['close'] = df['close'].astype(float)
            return df
        else:
            print(f'Dados inválidos para {symbol}')
            return None
    else:
        print(f'Erro ao buscar candles de {symbol}: {response.text}')
        return None

def calculate_rsi(df, period=14):
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def analyze_symbol(symbol):
    df_5m = get_klines(symbol, '5m')
    df_15m = get_klines(symbol, '15m')
    
    if df_5m is not None and df_15m is not None:
        rsi_5m = calculate_rsi(df_5m).iloc[-1]
        rsi_15m = calculate_rsi(df_15m).iloc[-1]
        
        # Sinais 5m
        if rsi_5m <= 30:
            send_telegram_alert(f'🟢 SINAL DE COMPRA (5m) - {symbol} - RSI: {round(rsi_5m,2)}')
        elif rsi_5m >= 70:
            send_telegram_alert(f'🔴 SINAL DE VENDA (5m) - {symbol} - RSI: {round(rsi_5m,2)}')

        # Sinais 15m
        if rsi_15m <= 30:
            send_telegram_alert(f'🟢 SINAL DE COMPRA (15m) - {symbol} - RSI: {round(rsi_15m,2)}')
        elif rsi_15m >= 70:
            send_telegram_alert(f'🔴 SINAL DE VENDA (15m) - {symbol} - RSI: {round(rsi_15m,2)}')

def verify_signals():
    print('🔎 Verificando sinais...')
    for symbol in symbols:
        try:
            analyze_symbol(symbol)
        except Exception as e:
            print(f'Erro ao analisar {symbol}: {e}')

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    global chat_id
    data = request.get_json()

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')

        if text.lower() == '/start':
            send_telegram_alert('✅ Bot iniciado com sucesso!')
        elif text.lower() == '/status':
            send_telegram_alert('✅ Bot está ativo!')

    return {'ok': True}

@app.route('/')
def index():
    return 'Bot online!'

if __name__ == '__main__':
    while True:
        verify_signals()
        time.sleep(300)  # 5 minutos
