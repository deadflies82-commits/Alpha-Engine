import os
import sys
import ccxt

api_key = os.getenv("OKX_API_KEY", "").strip()
secret_key = os.getenv("OKX_SECRET_KEY", "").strip()
passphrase = os.getenv("OKX_PASSPHRASE", "").strip()

if not api_key or not secret_key or not passphrase:
    print("ERROR: Missing one or more GitHub Secrets (OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE).")
    sys.exit(1)

exchange = ccxt.okx({
    "apiKey": api_key,
    "secret": secret_key,
    "password": passphrase,
    "options": {"defaultType": "spot"},
})

exchange.set_sandbox_mode(True)

try:
    balance = exchange.fetch_balance()
    non_zero = {k: v for k, v in balance.get("free", {}).items() if v and v > 0}
    print("SUCCESS: Connected to OKX Demo Trading!")
    print("Available Demo Balances:", non_zero)
except Exception as e:
    print("ERROR: Connection failed ->", e)
    sys.exit(1)
