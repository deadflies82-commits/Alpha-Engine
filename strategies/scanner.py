import pandas as pd

class Scanner:
    def __init__(self, exchange, max_symbols=3):
        self.ex = exchange
        self.max_symbols = max_symbols

    def scan_opportunities(self):
        try:
            # Single API fetch for all tickers to protect rate limits
            tickers = self.ex.fetch_tickers()
            
            candidates = []
            for symbol, data in tickers.items():
                if ":USDT" in symbol or ("/USDT" in symbol and "USDT/USDT" not in symbol):
                    quote_vol = data.get('quoteVolume') or 0
                    pct_change = data.get('percentage') or 0
                    
                    # Filter for institutional liquidity ($5M+ 24h volume)
                    if quote_vol >= 5_000_000:
                        candidates.append({
                            "symbol": symbol,
                            "volume": quote_vol,
                            "momentum": abs(pct_change)
                        })
            
            if not candidates:
                return ["SOL/USDT:USDT"]
                
            df = pd.DataFrame(candidates)
            df = df.sort_values(by="volume", ascending=False).head(15)
            df = df.sort_values(by="momentum", ascending=False)
            
            return df["symbol"].head(self.max_symbols).tolist()
            
        except Exception as e:
            print(f"[Scanner Warning] Scan failed: {e}. Defaulting to SOL/USDT.")
            return ["SOL/USDT:USDT"]
