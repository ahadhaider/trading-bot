# Algo Trading Bot — Setup Guide

## ⚠️ Zaroori Disclaimer
Ye code educational/technical starting point hai, financial advice nahi.
- Pehle **hamesha `MODE = "paper"`** par test karo (config.py me)
- Kam se kam 1-2 mahine paper trading me results dekho
- Real money (`MODE = "live"`) par tabhi jao jab risk samajhte ho aur
  jitna nuksan uthana afford kar sakte ho utna hi capital lagao
- Koi bhi automated bot 100% loss-proof nahi hota

## Files kya karti hain
| File | Kaam |
|---|---|
| `config.py` | Saari settings — symbols, risk limits, mode |
| `strategy.py` | Buy/Sell signal logic (SMA crossover + RSI) |
| `risk_manager.py` | Position sizing, stop-loss, daily loss limit — capital protect karta hai |
| `self_tune.py` | "Learning" module — purane data par best parameters dhoondhta hai |
| `broker_paper.py` | Paper trading (virtual money) — DEFAULT, safe |
| `broker_zerodha.py` | Live trading — Zerodha Kite Connect (baad me use karna) |
| `sheets_logger.py` | Google Sheet me har trade aur daily summary likhta hai |
| `main.py` | Sabko jodta hai — ye file run karo |

## ✅ Isko turant chalane ke liye (koi Google/Broker setup zaroori nahi)

Bot ab bina kisi setup ke chal sakta hai — CSV files me automatically log
karega (`logs/trades.csv`, `logs/daily_summary.csv`). Bas ye 2 steps:

```
pip install -r requirements.txt
python main.py
```

Google Sheets sirf tab activate hoga jab aap `credentials.json` daaloge —
warna bot khud CSV par fallback ho jaata hai (`combined_logger.py` ye
handle karta hai). Ye maine test bhi kar liya hai — [Testing](#testing-jo-maine-khud-kiya) section dekho.

## Setup Steps

### 1. Python packages install karo
```
pip install -r requirements.txt
```

### 2. Google Sheets connect karo (OPTIONAL — nahi karoge to bhi CSV me log hota rahega)
1. https://console.cloud.google.com par jao → naya project banao
2. "Google Sheets API" aur "Google Drive API" enable karo
3. "APIs & Services → Credentials" → Service Account banao
4. Uski JSON key download karo → naam `credentials.json` rakho → isi folder me daalo
5. Google Sheets me ek naya sheet banao, naam do (config.py ke `GOOGLE_SHEET_NAME` jaisa)
6. `credentials.json` ke andar jo `client_email` hai, us email ko apni Sheet me
   **Editor** access ke saath Share karo

### 3. Paper trading start karo
`config.py` me `MODE = "paper"` rakho (default already hai), phir:
```
python main.py
```
Ye market hours (9:15 AM – 3:30 PM) me chalega, signals generate karega,
virtual trades lega, aur sab Google Sheet me log karega. 3:15 PM ke baad
saari open positions automatically square-off ho jaayengi.

### 4. "Learning"/self-tuning chalao (weekly ya monthly)
```python
from broker_paper import get_historical_candles
from self_tune import apply_best_parameters

data = get_historical_candles("RELIANCE", period="60d")
apply_best_parameters(data)
```
Ye purane data par test karke best SMA/RSI settings dhoondh kar
`config.py` ke values ko runtime me update kar deta hai.

### 5. Live trading (sirf tab, jab ready ho)
1. `pip install kiteconnect`
2. Zerodha Kite Connect app banao (developer console), API key/secret lo
3. `config.py` me `KITE_API_KEY`, `KITE_API_SECRET` bharo
4. Roz login flow se `KITE_ACCESS_TOKEN` generate karo
5. `config.py` me `MODE = "live"` karo
6. **Chhote capital se shuru karo**

## Isko 24/7 automatic chalane ke liye
- Apne laptop ko chalu rakhna practical nahi hai — isliye ek cloud server
  use karo (AWS EC2 / DigitalOcean / PythonAnywhere)
- Server par `python main.py` ko `cron` ya `systemd service` se schedule karo
  taaki market open hote hi automatically start ho jaaye
- Errors track karne ke liye logs check karte raho — bina supervision ke
  hafton tak na chodo

## Testing jo maine khud kiya
Maine synthetic (fake) price data se poori pipeline chala kar test kiya:
1. Strategy signal generation ✅
2. Risk manager — position sizing, stop-loss/target hit, trade close ✅
3. Daily loss limit — sahi tarike se trading halt karta hai ✅
4. Local CSV logging — bina Google Sheets ke bhi kaam karta hai ✅
5. Self-tuning — parameter search sahi best combination dhoondhta hai ✅

Sab pass hue. Note: real market data (yfinance/Zerodha) is environment
me test nahi kar saka kyunki mujhe yahan internet access nahi hai — wo
part aapko apne system par pehli baar chalate waqt verify karna hoga.

## Kya maine set up kiya vs kya aapko khud karna hoga
**Maine kiya (code fully wired aur tested):**
- Poora bot logic — strategy, risk management, logging, self-tuning
- Zero-setup local CSV logging (turant chalega)
- Google Sheets integration (optional, connect karne par auto-activate)

**Aapko khud karna hoga (kyunki ye aapki personal identity/account maangte hain, main inke liye login nahi kar sakta):**
- Google Cloud service account banake `credentials.json` lena (agar Sheets chahiye)
- Zerodha (ya jo broker use karo) ka trading account aur API subscription lena
- Apne system par `pip install -r requirements.txt` chalana (internet chahiye, jo mere paas is environment me nahi hai)
- Server/cloud par 24/7 deploy karna agar chahte ho ki laptop band hone par bhi chale

## Next Improvements (jab basic version chal jaaye)
- Telegram/WhatsApp alerts jab trade open/close ho
- Multiple strategies (breakout, mean-reversion) ek saath run karke best perform karne wali ko weight dena
- Proper backtesting framework (backtrader / vectorbt) se pehle historical validate karna
