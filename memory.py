import json
import os

MEMORY_FILE = "execution_memory.json"

def load_failure_memory():
    """Loads execution memory from disk, or initializes it if missing."""
    if not os.path.exists(MEMORY_FILE):
        initial_data = {
            "blacklisted_tokens": [],
            "failed_wallets": [],
            "error_counts": {}
        }
        with open(MEMORY_FILE, "w") as f:
            json.dump(initial_data, f, indent=4)
        return initial_data
        
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading memory file: {e}")
        return {"blacklisted_tokens": [], "failed_wallets": [], "error_counts": {}}

def is_blacklisted(token_address):
    """Checks if a target token is permanently blacklisted in memory."""
    memory = load_failure_memory()
    return token_address in memory.get("blacklisted_tokens", [])

def record_mistake(token_address=None, wallet_address=None, error_type="UNKNOWN_ERROR"):
    """Permanently logs failures into execution_memory.json."""
    memory = load_failure_memory()
    
    if token_address and token_address not in memory["blacklisted_tokens"]:
        memory["blacklisted_tokens"].append(token_address)
        print(f"🧠 [Memory Updated] Token blacklisted: {token_address}")
        
    if wallet_address and wallet_address not in memory["failed_wallets"]:
        memory["failed_wallets"].append(wallet_address)
        print(f"🧠 [Memory Updated] Wallet blacklisted: {wallet_address}")
        
    memory["error_counts"][error_type] = memory["error_counts"].get(error_type, 0) + 1
    
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=4)
        print("💾 Execution memory successfully saved to disk.")
    except Exception as e:
        print(f"❌ Failed to save execution memory: {e}")
