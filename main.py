"""
main.py
Bot ka main loop. Ye:
1. Har symbol ka latest data leta hai
2. Strategy se signal nikaalta hai
3. Risk manager se check karwata hai
4. Order place karta hai (paper ya live, config.MODE ke hisaab se)
5. Google Sheet me sab log karta hai
6. Intraday square-off time par sab positions close kar deta hai

Chalane ka tarika:
    python main.py

NOTE: Ye ek continuous loop hai jo market hours me chalta rehta hai.
Isko chhodne ke liye Ctrl+C dabao.
"""

import time
import datetime
import config
import strategy
import risk_manager

if config.MODE == "paper":
    import broker_paper as broker
else:
    import broker_zerodha as broker

from combined_logger import CombinedLogger


def is_market_open():
    now = datetime.datetime.now().time()
    open_t = datetime.datetime.strptime(config.MARKET_OPEN_TIME, "%H:%M").time()
    close_t = datetime.datetime.strptime(config.MARKET_CLOSE_TIME, "%H:%M").time()
    return open_t <= now <= close_t


def is_square_off_time():
    now = datetime.datetime.now().time()
    sq_t = datetime.datetime.strptime(config.INTRADAY_SQUARE_OFF_TIME, "%H:%M").time()
    return now >= sq_t


def run():
    rm = risk_manager.RiskManager(config.STARTING_CAPITAL)
    rm.reset_day()
    logger = CombinedLogger()
    trades_today = 0

    print(f"=== Bot start ho gaya | MODE={config.MODE} | Capital={rm.capital} ===")

    while True:
        if not is_market_open():
            print("Market band hai. Wait kar rahe hain...")
            time.sleep(60)
            continue

        # Square-off time par sab positions close karo
        if is_square_off_time():
            for symbol in list(rm.open_positions.keys()):
                price = broker.get_latest_price(symbol)
                trade = rm.close_trade(symbol, price)
                broker.place_order(symbol, "SELL" if trade["side"] == "BUY" else "BUY",
                                    trade["qty"], price)
                if logger:
                    logger.log_trade(trade, reason="Square-off")
                print(f"[SQUARE-OFF] {trade}")
            print("Aaj ke liye trading khatam.")
            if logger:
                logger.log_daily_summary(datetime.date.today(), rm.day_start_capital,
                                          rm.capital, trades_today)
            break

        rm.check_daily_loss_limit()

        for symbol in config.SYMBOLS:
            try:
                # --- Existing position ka SL/Target check ---
                if symbol in rm.open_positions:
                    price = broker.get_latest_price(symbol)
                    hit = rm.check_sl_target(symbol, price)
                    if hit:
                        trade = rm.close_trade(symbol, price)
                        side_to_close = "SELL" if trade["side"] == "BUY" else "BUY"
                        broker.place_order(symbol, side_to_close, trade["qty"], price)
                        if logger:
                            logger.log_trade(trade, reason=hit)
                        trades_today += 1
                        print(f"[{hit}] {trade}")
                    continue

                # --- Naya signal check ---
                can_trade, msg = rm.can_open_new_trade(symbol)
                if not can_trade:
                    continue

                candles = broker.get_historical_candles(symbol)
                signal = strategy.generate_signal(candles)

                if signal in ("BUY", "SELL"):
                    price = broker.get_latest_price(symbol)
                    stop_loss_price = (
                        price * (1 - config.STOP_LOSS_PCT / 100)
                        if signal == "BUY"
                        else price * (1 + config.STOP_LOSS_PCT / 100)
                    )
                    qty = rm.calc_position_size(price, stop_loss_price)
                    if qty <= 0:
                        continue

                    broker.place_order(symbol, signal, qty, price)
                    pos = rm.open_trade(symbol, signal, qty, price)
                    print(f"[OPEN] {symbol} {signal} qty={qty} @ {price} | SL={pos['stop_loss']:.2f} Target={pos['target']:.2f}")

            except Exception as e:
                print(f"[ERROR] {symbol}: {e}")

        time.sleep(30)   # 30 second polling interval — apni zaroorat ke hisaab se adjust karo


if __name__ == "__main__":
    run()
