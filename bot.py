import requests
import time
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

stocks = ["SBIN", "ICICIBANK", "TATASTEEL"]

price_history = {s: [] for s in stocks}
nifty_history = []

def get_price(symbol):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://nse-api-ruby.vercel.app/stock?symbol={symbol}"
        data = requests.get(url, headers=headers).json()
        return float(data["data"]["last_price"])
    except:
        return None

def get_nifty():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = "https://nse-api-ruby.vercel.app/index?symbol=NIFTY%2050"
        data = requests.get(url, headers=headers).json()
        return float(data["data"]["last_price"])
    except:
        return None

def avg(x):
    return sum(x)/len(x)

def strike(price):
    return int(round(price/10)*10)

while True:

    nifty = get_nifty()
    if nifty:
        nifty_history.append(nifty)
        if len(nifty_history) > 10:
            nifty_history.pop(0)

    if len(nifty_history) < 5:
        time.sleep(60)
        continue

    market = "BULLISH" if nifty > avg(nifty_history) else "BEARISH"

    for stock in stocks:
        price = get_price(stock)
        if not price:
            continue

        price_history[stock].append(price)
        if len(price_history[stock]) > 10:
            price_history[stock].pop(0)

        data = price_history[stock]
        if len(data) < 6:
            continue

        avg_price = avg(data[:-1])
        high = max(data[:-1])
        low = min(data[:-1])

        st = strike(price)

        if price > high and price > avg_price and market == "BULLISH":
            send(f"{stock} 🚨 BUY CALL ({st} CE)\nPrice: {price}\nTrend: {market}")

        elif price < low and price < avg_price and market == "BEARISH":
            send(f"{stock} 🚨 BUY PUT ({st} PE)\nPrice: {price}\nTrend: {market}")

    time.sleep(60)