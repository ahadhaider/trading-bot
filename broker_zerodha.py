"""
broker_zerodha.py
Real/live trading ke liye Zerodha Kite Connect wrapper.
SIRF TAB USE KARO jab paper trading me kaafi test kar chuke ho aur
apni risk samajhte ho. Real paise ka nuksan ho sakta hai.

Setup: pip install kiteconnect, aur config.py me API key/secret/access
token bharo. Access token daily generate karna padta hai (login flow).
"""

from kiteconnect import KiteConnect
import config

kite = KiteConnect(api_key=config.KITE_API_KEY)
kite.set_access_token(config.KITE_ACCESS_TOKEN)


def get_historical_candles(symbol: str, interval="5minute", days=5):
    instrument_token = _get_instrument_token(symbol)
    import datetime
    to_date = datetime.datetime.now()
    from_date = to_date - datetime.timedelta(days=days)
    data = kite.historical_data(instrument_token, from_date, to_date, interval)
    import pandas as pd
    df = pd.DataFrame(data)
    df = df.rename(columns={"close": "close", "open": "open", "high": "high", "low": "low"})
    return df[["close", "open", "high", "low", "volume"]]


def get_latest_price(symbol: str) -> float:
    quote = kite.quote([f"NSE:{symbol}"])
    return quote[f"NSE:{symbol}"]["last_price"]


def place_order(symbol, side, qty, price=None):
    """Real order Zerodha ko bhejta hai. SAMBHAL KE."""
    transaction_type = kite.TRANSACTION_TYPE_BUY if side == "BUY" else kite.TRANSACTION_TYPE_SELL
    order_id = kite.place_order(
        variety=kite.VARIETY_REGULAR,
        exchange=kite.EXCHANGE_NSE,
        tradingsymbol=symbol,
        transaction_type=transaction_type,
        quantity=qty,
        order_type=kite.ORDER_TYPE_MARKET,
        product=kite.PRODUCT_MIS,   # intraday
    )
    return {"status": "success", "order_id": order_id}


def _get_instrument_token(symbol):
    instruments = kite.instruments("NSE")
    for inst in instruments:
        if inst["tradingsymbol"] == symbol:
            return inst["instrument_token"]
    raise ValueError(f"{symbol} ka instrument token nahi mila.")
