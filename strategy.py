def calculate_rsi(prices, period=14):
    """Pure Python mein RSI calculate karta hai bina kisi pandas/numpy ke."""
    if len(prices) < period + 1:
        return 50.0  # Default neutral RSI
    
    gains = 0.0
    losses = 0.0
    
    for i in range(1, period + 1):
        change = prices[i] - prices[i - 1]
        if change > 0:
            gains += change
        else:
            losses -= change
            
    avg_gain = gains / period
    avg_loss = losses / period
    
    if avg_loss == 0:
        return 100.0
        
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi

def calculate_ema(prices, period):
    """Pure Python mein EMA (Exponential Moving Average) calculate karta hai."""
    if not prices:
        return 0.0
    multiplier = 2 / (period + 1)
    ema = prices[0]
    for price in prices[1:]:
        ema = (price - ema) * multiplier + ema
    return ema

def decide_trade(candles):
    """
    RSI aur MACD Crossover ke basis par pure Python se smart signal generate karta hai.
    """
    if len(candles) < 30:
        return "HOLD", 50.0

    closes = [c['close'] for c in candles]
    
    # 1. RSI calculation
    current_rsi = calculate_rsi(closes)
    
    # 2. MACD Crossover calculation using EMA
    fast_ema_curr = calculate_ema(closes[-15:], 12)
    slow_ema_curr = calculate_ema(closes[-30:], 26)
    current_macd = fast_ema_curr - slow_ema_curr
    
    fast_ema_prev = calculate_ema(closes[-16:-1], 12)
    slow_ema_prev = calculate_ema(closes[-31:-1], 26)
    prev_macd = fast_ema_prev - slow_ema_prev
    
    signal_line_curr = current_macd * 0.9  # Simplified signal line
    signal_line_prev = prev_macd * 0.9

    bullish_crossover = (prev_macd <= signal_line_prev) and (current_macd > signal_line_curr)
    bearish_crossover = (prev_macd >= signal_line_prev) and (current_macd < signal_line_curr)

    # Smart Strategy Rules:
    if current_rsi < 45 and bullish_crossover:
        return "BUY", current_rsi
    elif current_rsi > 55 and bearish_crossover:
        return "SELL", current_rsi

    return "HOLD", current_rsi

if __name__ == "__main__":
    dummy_candles = [{"close": 100 + i} for i in range(40)]
    print("Strategy Test Signal:", decide_trade(dummy_candles))
