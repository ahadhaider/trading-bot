import json
import os
import csv

HISTORY_FILE = "logs/trades.csv"
LEARNING_CONFIG = "smart_weights.json"

def analyze_and_tune():
    """
    Pichle trades ke logs ko analyze karke bot ke parameters ko 
    automatically tune karta hai.
    """
    if not os.path.exists(HISTORY_FILE):
        return {"status": "No data", "adjustment": "Default"}

    total_trades = 0
    winning_trades = 0
    total_pnl = 0.0

    try:
        with open(HISTORY_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_trades += 1
                try:
                    pnl = float(row.get("PnL", 0))
                    total_pnl += pnl
                    if pnl > 0:
                        winning_trades += 1
                except ValueError:
                    pass
    except Exception as e:
        return {"status": "Error reading logs"}

    win_rate = (winning_trades / total_trades) if total_trades > 0 else 0.0
    
    tuning_state = {
        "total_analyzed_trades": total_trades,
        "win_rate": round(win_rate * 100, 2),
        "net_pnl": round(total_pnl, 2),
        "strategy_bias": "AGGRESSIVE" if win_rate > 0.6 else ("CONSERVATIVE" if win_rate < 0.4 else "BALANCED"),
        "risk_multiplier": 1.0 if win_rate >= 0.5 else 0.8
    }

    with open(LEARNING_CONFIG, "w") as f:
        json.dump(tuning_state, f, indent=2)

    return tuning_state

if __name__ == "__main__":
    print(analyze_and_tune())
