import json
import os
import config

STATE_FILE = "state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "capital": config.STARTING_CAPITAL,
        "day_start_capital": config.STARTING_CAPITAL,
        "open_positions": {},
        "trading_halted": False,
    }

def save_state(rm):
    state = {
        "capital": rm.capital,
        "day_start_capital": rm.day_start_capital,
        "open_positions": rm.open_positions,
        "trading_halted": rm.trading_halted,
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def apply_state(rm, state):
    rm.capital = state["capital"]
    rm.day_start_capital = state["day_start_capital"]
    rm.open_positions = state["open_positions"]
    rm.trading_halted = state["trading_halted"]
    return rm
