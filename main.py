# main.py
# Project Alpha - Main Execution Runner

import asyncio
from risk import RiskEngine
from bot import AlphaBot
from memory import BatchMemory

async def main():
    print("--- Initializing Project Alpha Engine ---")
    
    # 1. Initialize our components with your $200 starting capital baseline
    risk_engine = RiskEngine(account_balance=200.0, max_risk_pct=0.01, max_daily_drawdown_pct=0.02)
    bot = AlphaBot(risk_engine=risk_engine, symbol="SOL-PERP")
    memory = BatchMemory()
    
    # 2. Define our target batch parameters
    batch_id = "batch_001"
    batch_count = 10
    lot_size = 0.1
    target_profit = 6.0
    
    print(f"[SYSTEM] Starting Capital: ${risk_engine.account_balance:.2f}")
    print(f"[SYSTEM] Target Batch Profit: ${target_profit:.2f}")

    # 3. Trigger the batch entry (automatically runs the risk/fee check first)
    success = await bot.execute_batch_entry(
        batch_count=batch_count,
        lot_size=lot_size,
        estimated_gas_per_tx=0.0005,  # Estimated network fee per tx
        max_slippage=0.02,             # Allowed slippage buffer
        target_profit=target_profit
    )

    if success:
        # 4. Register active positions in memory.py
        memory.register_batch(batch_id, bot.active_batch)
        print(f"[MEMORY] Registered batch {batch_id} with {len(bot.active_batch)} positions.")

        # 5. Run the background watchdog loop to monitor aggregate PnL and bulk-exit
        await bot.monitor_and_bulk_exit(target_profit=target_profit)
        
        # 6. Clear out state memory once the bulk-exit completes
        memory.clear_batch(batch_id)
        print(f"[MEMORY] Cleared batch {batch_id}. Cycle complete.")
    else:
        print("[SYSTEM] Batch execution blocked by the Risk Defense Shield.")

if __name__ == "__main__":
    asyncio.run(main())
