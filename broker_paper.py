import urllib.request
import json

def get_historical_candles(symbol="RELIANCE", period="5d", interval="1d"):
    try:
        # Append .NS for Indian stocks if not already present
        formatted_symbol = symbol if "." in symbol else f"{symbol}.NS"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{formatted_symbol}?range={period}&interval={interval}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
            valid_prices = [p for p in prices if p is not None]
            if valid_prices:
                return valid_prices
    except Exception as e:
        print(f"[ERROR] Failed to fetch historical candles for {symbol}: {e}")
    return [100, 102, 101, 105, 107, 106, 110, 112, 115, 113, 116, 118, 120, 122, 125]

def get_latest_price(symbol="RELIANCE"):
    candles = get_historical_candles(symbol, period="1d", interval="1m")
    return candles[-1] if candles else 150.0

def execute_trade(symbol, action, quantity, price):
    print(f"[PAPER TRADE] Executed {action} {quantity} shares of {symbol} at ${price}")
    return True
