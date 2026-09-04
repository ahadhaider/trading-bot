"""
config.py
Sab settings yahan par hain. Ye file edit karke aap symbols, risk limits,
Google Sheet details, aur mode (paper / live) set kar sakte ho.
"""

# ---------------- MODE ----------------
# "paper"  -> virtual money, koi real order nahi jaayega (SAFE, start yahin se)
# "live"   -> real broker API se real order jaayega (sirf paper me test karne
#             ke baad, aur apni risk par use karo)
MODE = "paper"

# ---------------- SYMBOLS ----------------
# NSE symbols jo bot track karega
SYMBOLS = ["RELIANCE", "TCS", "INFY", "HDFCBANK"]

# ---------------- CAPITAL & RISK ----------------
STARTING_CAPITAL = 100000          # paper trading starting virtual capital (INR)
MAX_RISK_PER_TRADE_PCT = 1.0       # ek trade me capital ka max kitna % risk hoga
MAX_DAILY_LOSS_PCT = 3.0           # din bhar me itna % loss hone par bot trading band kar dega
MAX_POSITION_PCT = 20.0            # ek symbol me capital ka max kitna % lagega
STOP_LOSS_PCT = 1.5                # har trade ka stop loss (%)
TARGET_PCT = 3.0                   # har trade ka target (%)

# ---------------- STRATEGY PARAMETERS ----------------
# Ye default values hain — "learning" module inhe periodically backtest
# karke better values se update karta hai (self_tune.py dekho)
SHORT_MA = 9
LONG_MA = 21
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# ---------------- INTRADAY TIMING ----------------
INTRADAY_SQUARE_OFF_TIME = "15:15"   # is time ke baad saare open positions close
MARKET_OPEN_TIME = "09:15"
MARKET_CLOSE_TIME = "15:30"

# ---------------- GOOGLE SHEETS ----------------
GOOGLE_SHEET_NAME = "Algo_Trading_Log"     # aapki Google Sheet ka naam
GOOGLE_CREDS_FILE = "credentials.json"      # service account JSON file ka path

# ---------------- BROKER (sirf MODE="live" ke liye) ----------------
# Zerodha Kite Connect credentials (live mode me use hote hain)
KITE_API_KEY = "YOUR_API_KEY"
KITE_API_SECRET = "YOUR_API_SECRET"
KITE_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"    # daily generate hota hai
