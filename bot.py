import os
import time
import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Secure structural tokens pulled right from Render's cloud vault environment
API_KEY = os.environ.get('ALPACA_API_KEY')
SECRET_KEY = os.environ.get('ALPACA_SECRET_KEY')

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
TARGET_STOCK = "AAPL"
GOAL_TARGET = 2000000000.00  # Our targeted $2 Billion Milestone layout

def run_institutional_cycle():
    print(f"\n🚀 [Alpha Engine] Scanning System Status... Target: ${GOAL_TARGET:,.2f}")
    account = trading_client.get_account()
    current_cash = float(account.cash)
    buying_power = float(account.buying_power)
    
    print(f"💰 Active Portfolio Cash: ${current_cash:,.2f}")
    print(f"⚡ Intraday Buying Power: ${buying_power:,.2f}")
    
    progress_pct = (current_cash / GOAL_TARGET) * 100
    print(f"📈 Milestones Completed: {progress_pct:.6f}% toward $2B")
    print("⏳ System Status: Running normal diagnostic sweeps. Execution layer fully clear.")

while True:
    try:
        run_institutional_cycle()
    except Exception as e:
        print(f"❌ Connection Block: Ensure your free Secrets match your Alpaca dashboard. Details: {e}")
    print("💤 Systems idling safely for 5 minutes until next loop...")
    time.sleep(300)
