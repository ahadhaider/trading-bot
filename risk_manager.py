"""
risk_manager.py
Ye module capital protect karta hai. Koi bhi trade isse pass hue bina jaa nahi sakta.
Yahi wo layer hai jo bot ko "sab uda dena" se bachata hai.
"""

import config


class RiskManager:
    def __init__(self, starting_capital):
        self.capital = starting_capital
        self.day_start_capital = starting_capital
        self.open_positions = {}   # symbol -> {qty, entry_price, stop_loss, target}
        self.trading_halted = False

    def reset_day(self):
        """Naye trading din ki shuruaat me call karo."""
        self.day_start_capital = self.capital
        self.trading_halted = False

    def daily_loss_pct(self):
        loss = self.day_start_capital - self.capital
        return (loss / self.day_start_capital) * 100 if self.day_start_capital else 0

    def check_daily_loss_limit(self):
        """Agar din ka loss limit se zyada ho gaya to trading rok do."""
        if self.daily_loss_pct() >= config.MAX_DAILY_LOSS_PCT:
            self.trading_halted = True
        return self.trading_halted

    def calc_position_size(self, entry_price, stop_loss_price):
        """
        Position size aise calculate karta hai ki agar stop loss hit ho
        to loss = capital ka MAX_RISK_PER_TRADE_PCT se zyada na ho.
        """
        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share <= 0:
            return 0

        max_risk_amount = self.capital * (config.MAX_RISK_PER_TRADE_PCT / 100)
        qty_by_risk = int(max_risk_amount / risk_per_share)

        max_position_value = self.capital * (config.MAX_POSITION_PCT / 100)
        qty_by_position_cap = int(max_position_value / entry_price)

        return max(min(qty_by_risk, qty_by_position_cap), 0)

    def can_open_new_trade(self, symbol):
        if self.trading_halted:
            return False, "Daily loss limit hit — trading halted for today."
        if symbol in self.open_positions:
            return False, f"{symbol} me already open position hai."
        return True, "OK"

    def open_trade(self, symbol, side, qty, entry_price):
        stop_loss = (
            entry_price * (1 - config.STOP_LOSS_PCT / 100)
            if side == "BUY"
            else entry_price * (1 + config.STOP_LOSS_PCT / 100)
        )
        target = (
            entry_price * (1 + config.TARGET_PCT / 100)
            if side == "BUY"
            else entry_price * (1 - config.TARGET_PCT / 100)
        )
        self.open_positions[symbol] = {
            "side": side,
            "qty": qty,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": target,
        }
        return self.open_positions[symbol]

    def close_trade(self, symbol, exit_price):
        pos = self.open_positions.pop(symbol, None)
        if not pos:
            return None
        if pos["side"] == "BUY":
            pnl = (exit_price - pos["entry_price"]) * pos["qty"]
        else:
            pnl = (pos["entry_price"] - exit_price) * pos["qty"]
        self.capital += pnl
        return {
            "symbol": symbol,
            "side": pos["side"],
            "qty": pos["qty"],
            "entry_price": pos["entry_price"],
            "exit_price": exit_price,
            "pnl": round(pnl, 2),
            "capital_after": round(self.capital, 2),
        }

    def check_sl_target(self, symbol, current_price):
        """Return 'SL', 'TARGET', or None"""
        pos = self.open_positions.get(symbol)
        if not pos:
            return None
        if pos["side"] == "BUY":
            if current_price <= pos["stop_loss"]:
                return "SL"
            if current_price >= pos["target"]:
                return "TARGET"
        else:
            if current_price >= pos["stop_loss"]:
                return "SL"
            if current_price <= pos["target"]:
                return "TARGET"
        return None
