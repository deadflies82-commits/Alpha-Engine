"""
Crypto bot skeleton: GitHub-optimized modular orchestration engine.
PAPER mode by default: simulates trades locally without sending real orders.
"""
import importlib, logging, os, sys, time
import ccxt
import pandas as pd

# --- GITHUB REPOSITORY PATH RESOLUTION ---
# Guarantees Python finds the 'strategies' package regardless of working directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
# ----------------------------------------

CONFIG = dict(
    exchange="bybit",          # CCXT exchange endpoint
    testnet=True,              # True = exchange testnet sandbox
    paper=True,                # True = local paper trading simulation
    paper_equity=200.0,        # Starting balance aligned with your $200 baseline
    max_gross_leverage=1.0,    # Maximum gross exposure cap
    max_daily_loss=0.03,       # -3% daily drawdown hard-halt circuit breaker
    min_order_usd=5.0,         # Minimum order size filter
)
log = logging.getLogger("bot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

# Timeframe dictionary updated for high-frequency M1/M5 scalping loops
TF_SEC = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400
}


class Bot:
    def __init__(self, strategy, cfg=CONFIG):
        self.s, self.cfg = strategy, cfg
        self.ex = getattr(ccxt, cfg["exchange"])({
            "apiKey": os.getenv("EXCHANGE_KEY"),
            "secret": os.getenv("EXCHANGE_SECRET"),
            "options": {"defaultType": "swap"},   # Perpetual futures swaps
        })
        if cfg["testnet"]:
            self.ex.set_sandbox_mode(True)
        self.paper_pos, self.paper_eq = {}, cfg["paper_equity"]
        self.last_px, self.day, self.day_start_eq = {}, None, None

    def candles(self, symbol, limit):
        raw = self.ex.fetch_ohlcv(symbol, self.s.timeframe, limit=limit + 1)
        df = pd.DataFrame(raw, columns=["ts", "open", "high", "low", "close", "volume"])
        df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
        df = df.set_index("ts").iloc[:-1]       # Drop unfinished candle to prevent lookahead bias
        age = (pd.Timestamp.now(tz="UTC") - df.index[-1]).total_seconds()
        if age > 3 * TF_SEC[self.s.timeframe]:
            raise RuntimeError(f"{symbol}: data is {age:.0f}s stale")
        return df

    def equity(self):
        if self.cfg["paper"]:
            return self.paper_eq
        return float(self.ex.fetch_balance()["USDT"]["total"])

    def positions(self):
        if self.cfg["paper"]:
            return dict(self.paper_pos)
        pos = {}
        for p in self.ex.fetch_positions(self.s.symbols):
            qty = float(p["contracts"] or 0) * float(p.get("contractSize") or 1)
            pos[p["symbol"]] = qty if p["side"] == "long" else -qty
        return pos

    def mark_paper(self, prices):
        for sym, qty in self.paper_pos.items():
            if sym in self.last_px:
                self.paper_eq += qty * (prices[sym] - self.last_px[sym])
        self.last_px = dict(prices)

    def risk_ok(self, eq):
        today = pd.Timestamp.now(tz="UTC").date()
        if today != self.day:
            self.day, self.day_start_eq = today, eq
        if eq < self.day_start_eq * (1 - self.cfg["max_daily_loss"]):
            log.error("Daily loss limit hit -> closing everything and stopping")
            return False
        return True

    def trade(self, symbol, qty):
        side = "buy" if qty > 0 else "sell"
        if self.cfg["paper"]:
            self.paper_pos[symbol] = self.paper_pos.get(symbol, 0.0) + qty
            log.info(f"[PAPER] {side} {abs(qty):.6f} {symbol}")
            return
        amount = float(self.ex.amount_to_precision(symbol, abs(qty)))
        if amount > 0:
            self.ex.create_order(symbol, "market", side, amount)
            log.info(f"[LIVE] {side} {amount} {symbol}")

    def rebalance(self, weights, prices, eq):
        gross = sum(abs(w) for w in weights.values())
        cap = self.cfg["max_gross_leverage"]
        if gross > cap:
            weights = {k: w * cap / gross for k, w in weights.items()}
        cur = self.positions()
        for sym in set(weights) | set(cur):
            target = weights.get(sym, 0.0) * eq / prices[sym]
            delta = target - cur.get(sym, 0.0)
            if abs(delta) * prices[sym] >= self.cfg["min_order_usd"]:
                self.trade(sym, delta)

    def flatten(self, prices):
        for sym, qty in self.positions().items():
            if qty:
                self.trade(sym, -qty)

    def run(self):
        while True:
            try:
                data = {s: self.candles(s, self.s.history) for s in self.s.symbols}
                prices = {s: float(df["close"].iloc[-1]) for s, df in data.items()}
                if self.cfg["paper"]:
                    self.mark_paper(prices)
                eq = self.equity()
                if not self.risk_ok(eq):
                    self.flatten(prices)
                    break
                weights = self.s.target_weights(data)
                log.info(f"equity={eq:.2f} weights={weights}")
                self.rebalance(weights, prices, eq)
            except Exception as e:
                log.exception(f"Loop error, changing nothing: {e}")
            time.sleep(TF_SEC[self.s.timeframe])


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "sol_scalper"
    Strategy = importlib.import_module(f"strategies.{name}").Strategy
    Bot(Strategy()).run()
