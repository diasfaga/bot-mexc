import os
import time
import requests
import pandas as pd
from flask import Flask, request

app = Flask(__name__)

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

MEXC_BASE_URL = 'https://api.mexc.com'

ALTCOINS = [
    "1000PEPEUSDT", "1000SATSUSDT", "AGIXUSDT", "APTUSDT", "ARBUSDT", "ASTRUSDT",
    "BLURUSDT", "C98USDT", "CFXUSDT", "CHZUSDT", "CKBUSDT", "CROUSDT", "DASHUSDT",
    "DOGEUSDT", "DYDXUSDT", "ENAUSDT", "ENSUSDT", "FILUSDT", "FLOKIUSDT", "FTMUSDT",
    "GALAUSDT", "GMXUSDT", "ICPUSDT", "INJUSDT", "JOEUSDT", "LDOUSDT", "LINAUSDT",
    "LINKUSDT", "LTCUSDT", "MANAUSDT", "MASKUSDT", "NEARUSDT", "OPUSDT", "PEPEUSDT",
    "RNDRUSDT", "RPLUSDT", "SANDUSDT", "SFPUSDT", "STXUSDT", "SUIUSDT", "THETAUSDT",
    "TWTUSDT", "VETUSDT", "WLDUSDT", "WOOUSDT", "XLMUSDT", "XRPUSDT", "XTMUSDT",
    "ZILUSDT", "ZRXUSDT",
    "FARTCOINUSDT", "VIRTUALUSDT"
]

def calcular_rsi(data, period=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def buscar_candles(symbol, interval, limit=100):
    url = f"{MEXC_BASE_URL}/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df['close'] = pd.to_numeric(df['close'])
        return df
    except Exception as e:
        print(f"Erro ao buscar candles de {symbol}: {e}")
        return None

def detectar_sinal(df, symbol, interval):
    if df is None or df.empty:
        return None

    df['rsi'] = calcular_rsi(df)

    ultimo_rsi = df['rsi'].iloc[-1]
    ultimo_close = df['close'].iloc[-1]
    penultimo_close = df['close'].iloc[-2]

    sinal = None

    if ultimo_rsi < 30:
        sinal = f"🟢 {symbol} ({interval}) RSI ({round(ultimo_rsi,2)}) - Sobrevendido! (Possível COMPRA)"
    elif ultimo_rsi > 70:
        sinal = f"🔴 {symbol} ({interval}) RSI ({round(ultimo_rsi,2)}) - Sobrecomprado! (Possível VENDA)"
    elif ultimo_close > penultimo_close:
        sinal = f"🚀 {symbol} ({interval}) Rompimento pra CIMA detectado!"
    elif ultimo_close < penultimo_close:
        sinal = f"⚡ {symbol} ({interval}) Rompimento pra BAIXO detectado!"

    return sinal

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem no Telegram: {e}")

@app.route('/', methods=['POST', 'GET'])
def webhook():
    if request.method == 'POST':
        update = request.get_json()
        if 'message' in update and 'text' in update['message']:
            texto = update['message']['text']
            chat_id = update['message']['chat']['id']

            if texto.lower() == '/start':
                enviar_telegram("✅ Bot iniciado com sucesso!")
            elif texto.lower() == '/status':
                enviar_telegram("✅ Bot está ativo!")
        return 'ok'
    else:
        return 'Bot rodando.'

def checar_sinais():
    print("🔎 Carregando altcoins...")
    enviar_telegram("🔎 Carregando 50 melhores altcoins...")
    for symbol in ALTCOINS:
        for timeframe in ['5m', '15m']:
            df = buscar_candles(symbol, timeframe, limit=100)
            sinal = detectar_sinal(df, symbol, timeframe)
            if sinal:
                enviar_telegram(sinal)
            time.sleep(0.5)  # Pequena pausa para evitar flood de requisições

if __name__ == '__main__':
    from threading import Thread

    def loop_verificacao():
        while True:
            checar_sinais()
            time.sleep(300)  # 5 minutos (300 segundos)

    Thread(target=loop_verificacao).start()
    app.run(host='0.0.0.0', port=8080)
