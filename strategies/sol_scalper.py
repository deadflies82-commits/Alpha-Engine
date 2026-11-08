import pandas as pd
import numpy as np

class Strategy:
    def __init__(self):
        self.timeframe = "1m"             # M1 timeframe for high-frequency scalping
        self.symbols = ["SOL/USDT:USDT"]  # Primary perpetual swap target
        self.history = 50                 # Minimal lookback to preserve mobile RAM

    def target_weights(self, data):
        weights = {sym: 0.0 for sym in self.symbols}
        df = data.get(self.symbols[0])
        
        if df is None or len(df) < 30:
            return weights

        # 1. Fast Micro-Trend EMAs
        df['ema_fast'] = df['close'].ewm(span=5, adjust=False).mean()
        df['ema_slow'] = df['close'].ewm(span=13, adjust=False).mean()
        
        # 2. Relative Volume Spike Detection
        df['vol_ma'] = df['volume'].rolling(20).mean() + 1e-8
        df['rvol'] = df['volume'] / df['vol_ma']
        
        # 3. Average True Range (ATR) Volatility Check
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['atr'] = true_range.rolling(14).mean()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Dead market filter
        if latest['atr'] / latest['close'] < 0.0005:
            return weights
            
        # Entry Logic: EMA Crossover + Relative Volume Surge > 1.5x
        bullish_cross = (prev['ema_fast'] <= prev['ema_slow']) and (latest['ema_fast'] > latest['ema_slow'])
        bearish_cross = (prev['ema_fast'] >= prev['ema_slow']) and (latest['ema_fast'] < latest['ema_slow'])
        
        if bullish_cross and latest['rvol'] > 1.5:
            weights[self.symbols[0]] = 1.0
        elif bearish_cross and latest['rvol'] > 1.5:
            weights[self.symbols[0]] = -1.0
            
        return weights
