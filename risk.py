# risk.py
# Project Alpha - Risk Management & Pre-Trade Defense Shield

class RiskEngine:
    def __init__(self, account_balance=200.0, max_risk_pct=0.01, max_daily_drawdown_pct=0.02):
        self.account_balance = account_balance
        self.max_risk_pct = max_risk_pct  # 1% per-trade risk cap
        self.max_daily_drawdown_pct = max_daily_drawdown_pct  # 2% max daily loss limit
        self.daily_start_balance = account_balance

    def calculate_max_risk_amount(self):
        """Returns maximum allowed USD risk for a trade batch (1% of balance)."""
        return self.account_balance * self.max_risk_pct

    def evaluate_batch_viability(self, batch_count, estimated_gas_per_tx, max_slippage_usd, target_profit_usd):
        """
        Pre-execution math check:
        Ensures target profit strictly outpaces combined transaction fees and slippage.
        """
        # Gas for both entry and exit transactions across all micro-trades in the batch
        total_gas_cost = (estimated_gas_per_tx * batch_count) * 2
        total_slippage_buffer = max_slippage_usd * batch_count
        
        total_overhead = total_gas_cost + total_slippage_buffer
        net_expected_profit = target_profit_usd - total_overhead

        if net_expected_profit <= 0:
            return False, f"REJECTED: Overhead (${total_overhead:.4f}) exceeds target profit (${target_profit_usd:.2f})"
        
        return True, f"APPROVED: Net target after overhead is ${net_expected_profit:.4f}"

    def check_daily_drawdown(self, current_balance):
        """Circuit breaker: Halts trading if daily loss limit is hit."""
        max_allowed_loss = self.daily_start_balance * self.max_daily_drawdown_pct
        current_drawdown = self.daily_start_balance - current_balance
        
        if current_drawdown >= max_allowed_loss:
            return False, "CIRCUIT BREAKER: Daily drawdown limit reached. Halting trades."
        
        return True, "Risk status clear."
