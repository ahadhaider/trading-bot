"""
sheets_logger.py
Har trade aur roz ka summary Google Sheet me likhta hai.

Setup (ek baar karna hai):
1. https://console.cloud.google.com par jao -> new project banao
2. "Google Sheets API" aur "Google Drive API" enable karo
3. Service Account banao -> uski JSON key download karo -> naam do
   'credentials.json' -> isi folder me rakho
4. Google Sheet banao (naam config.py me GOOGLE_SHEET_NAME jaisa rakho)
5. Us Sheet ko service account ke email (credentials.json ke andar
   "client_email") ke saath Editor access me Share karo
"""

import datetime
import gspread
from google.oauth2.service_account import Credentials
import config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TRADE_HEADERS = ["Timestamp", "Symbol", "Side", "Qty", "Entry Price",
                  "Exit Price", "PnL", "Capital After", "Reason"]
SUMMARY_HEADERS = ["Date", "Starting Capital", "Ending Capital",
                    "Day PnL", "Day PnL %", "Trades Taken"]


class SheetsLogger:
    def __init__(self):
        creds = Credentials.from_service_account_file(config.GOOGLE_CREDS_FILE, scopes=SCOPES)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(config.GOOGLE_SHEET_NAME)
        self.trades_ws = self._get_or_create_worksheet("Trades", TRADE_HEADERS)
        self.summary_ws = self._get_or_create_worksheet("Daily Summary", SUMMARY_HEADERS)

    def _get_or_create_worksheet(self, title, headers):
        try:
            ws = self.sheet.worksheet(title)
        except gspread.WorksheetNotFound:
            ws = self.sheet.add_worksheet(title=title, rows=1000, cols=len(headers))
            ws.append_row(headers)
        return ws

    def log_trade(self, trade: dict, reason: str = ""):
        row = [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            trade["symbol"],
            trade["side"],
            trade["qty"],
            trade["entry_price"],
            trade["exit_price"],
            trade["pnl"],
            trade["capital_after"],
            reason,
        ]
        self.trades_ws.append_row(row)

    def log_daily_summary(self, date, start_capital, end_capital, trades_count):
        pnl = round(end_capital - start_capital, 2)
        pnl_pct = round((pnl / start_capital) * 100, 2) if start_capital else 0
        row = [str(date), start_capital, end_capital, pnl, pnl_pct, trades_count]
        self.summary_ws.append_row(row)
