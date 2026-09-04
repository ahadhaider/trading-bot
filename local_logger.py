"""
local_logger.py
Bina kisi setup ke turant kaam karne wala logger — trades aur daily
summary ko local CSV files me likhta hai (logs/ folder me).

Ye tab use hota hai jab Google Sheets connect nahi hai. Jaise hi aap
Google Sheets set up kar lo (credentials.json daal ke), main.py
automatically Google Sheets par switch ho jaayega — CSV bhi backup ke
liye chalta rahega.
"""

import csv
import os
import datetime

LOG_DIR = "logs"
TRADES_FILE = os.path.join(LOG_DIR, "trades.csv")
SUMMARY_FILE = os.path.join(LOG_DIR, "daily_summary.csv")

TRADE_HEADERS = ["Timestamp", "Symbol", "Side", "Qty", "Entry Price",
                  "Exit Price", "PnL", "Capital After", "Reason"]
SUMMARY_HEADERS = ["Date", "Starting Capital", "Ending Capital",
                    "Day PnL", "Day PnL %", "Trades Taken"]


class LocalLogger:
    def __init__(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        self._ensure_file(TRADES_FILE, TRADE_HEADERS)
        self._ensure_file(SUMMARY_FILE, SUMMARY_HEADERS)

    def _ensure_file(self, path, headers):
        if not os.path.exists(path):
            with open(path, "w", newline="") as f:
                csv.writer(f).writerow(headers)

    def log_trade(self, trade: dict, reason: str = ""):
        row = [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            trade["symbol"], trade["side"], trade["qty"],
            trade["entry_price"], trade["exit_price"], trade["pnl"],
            trade["capital_after"], reason,
        ]
        with open(TRADES_FILE, "a", newline="") as f:
            csv.writer(f).writerow(row)

    def log_daily_summary(self, date, start_capital, end_capital, trades_count):
        pnl = round(end_capital - start_capital, 2)
        pnl_pct = round((pnl / start_capital) * 100, 2) if start_capital else 0
        row = [str(date), start_capital, end_capital, pnl, pnl_pct, trades_count]
        with open(SUMMARY_FILE, "a", newline="") as f:
            csv.writer(f).writerow(row)
