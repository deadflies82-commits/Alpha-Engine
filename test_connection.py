import os
from dotenv import load_dotenv
import ccxt

# Load environment variables from .env
load_dotenv()

api_key = os.getenv("OKX_API_KEY")
secret_key = os.getenv("OKX_SECRET_KEY")
passphrase = os.getenv("OKX_PASSPHRASE")
flag = os.getenv("OKX_FLAG")

print(f"Loaded API Key: {api_key[:6]}... (truncated for safety)")
print(f"Demo Flag: {flag}")

# Initialize OKX exchange instance for demo trading
exchange = ccxt.okx({
    'apiKey': api_key,
    'secret': secret_key,
    'password': passphrase,
    'options': {
        'defaultType': 'spot',
    },
})

# Set sandbox/demo mode if flag is 1
if flag == "1":
    exchange.set_sandbox_mode(True)

try:
    # Test fetching balance
    balance = exchange.fetch_balance()
    print("SUCCESS: Connected to OKX successfully!")
    print("Account Balance:", balance['free'])
except Exception as e:
    print("ERROR: Connection failed ->", e)
