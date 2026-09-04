"""
combined_logger.py
Ek single logger jo:
- Hamesha local CSV me likhta hai (kabhi fail nahi hota, zero setup)
- Agar Google Sheets configured hai (credentials.json maujood hai), to
  wahan bhi likhta hai

Isse bot turant chalu ho jaata hai, aur Google Sheets sirf "bonus" hai
jab aap chaho tab add kar sakte ho.
"""

import os
from local_logger import LocalLogger
import config


class CombinedLogger:
    def __init__(self):
        self.local = LocalLogger()
        self.sheets = None

        if os.path.exists(config.GOOGLE_CREDS_FILE):
            try:
                from sheets_logger import SheetsLogger
                self.sheets = SheetsLogger()
                print(f"[Logger] Google Sheets connected: '{config.GOOGLE_SHEET_NAME}'")
            except Exception as e:
                print(f"[Logger] Google Sheets connect nahi ho paya ({e}). "
                      f"Sirf local CSV (logs/) use ho raha hai.")
        else:
            print(f"[Logger] '{config.GOOGLE_CREDS_FILE}' nahi mili — sirf local CSV "
                  f"(logs/trades.csv, logs/daily_summary.csv) me log ho raha hai. "
                  f"Google Sheets setup README me hai.")

    def log_trade(self, trade: dict, reason: str = ""):
        self.local.log_trade(trade, reason)
        if self.sheets:
            try:
                self.sheets.log_trade(trade, reason)
            except Exception as e:
                print(f"[Logger] Sheets trade log fail: {e}")

    def log_daily_summary(self, date, start_capital, end_capital, trades_count):
        self.local.log_daily_summary(date, start_capital, end_capital, trades_count)
        if self.sheets:
            try:
                self.sheets.log_daily_summary(date, start_capital, end_capital, trades_count)
            except Exception as e:
                print(f"[Logger] Sheets summary log fail: {e}")
