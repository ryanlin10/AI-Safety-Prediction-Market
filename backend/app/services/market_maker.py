"""
Automated Market Maker (AMM) for prediction markets
Uses a simplified Constant Product Market Maker (CPMM) similar to Uniswap
"""
import math
from typing import Dict, List
import json

class MarketMaker:
    """
    Automated Market Maker using constant product formula
    Price = shares_outcome / (shares_outcome + shares_other_outcomes)
    """
    
    def __init__(self, initial_liquidity: float = 1000.0):
        self.initial_liquidity = initial_liquidity
    
    def get_liquidity_pools(self, outcomes: List[str], bets: List) -> Dict[str, float]:
        """
        Calculate liquidity pools for each outcome based on bets
        Initial liquidity is split equally among outcomes
        """
        # Start with equal liquidity for each outcome
        pools = {outcome: self.initial_liquidity / len(outcomes) for outcome in outcomes}
        
        # Add bet amounts to respective pools
        for bet in bets:
            if bet.outcome in pools:
                pools[bet.outcome] += bet.stake
        
        return pools
    
    def calculate_price(self, outcome: str, pools: Dict[str, float]) -> float:
        """
        Calculate current price for an outcome
        Price = pool_outcome / total_pools
        """
        total = sum(pools.values())
        if total == 0:
            return 1.0 / len(pools)  # Equal probability if no liquidity
        
        return pools[outcome] / total
    
    def calculate_all_prices(self, outcomes: List[str], bets: List) -> Dict[str, float]:
        """Calculate prices for all outcomes"""
        pools = self.get_liquidity_pools(outcomes, bets)
        return {outcome: self.calculate_price(outcome, pools) for outcome in outcomes}
    
    def calculate_buy_price(self, outcome: str, amount: float, pools: Dict[str, float]) -> float:
        """
        Calculate how much it costs to buy 'amount' of shares for an outcome
        Uses constant product formula: (x + dx) * (y - dy) = x * y
        """
        if amount <= 0:
            return 0.0
        
        outcome_pool = pools[outcome]
        other_pools_total = sum(p for o, p in pools.items() if o != outcome)
        
        # Calculate cost using constant product formula
        # After buying, new outcome pool should satisfy: new_pool * other_pool = constant
        k = outcome_pool * other_pools_total  # Constant product
        
        # New outcome pool after buying
        new_outcome_pool = outcome_pool + amount
        
        # Calculate how much needs to be added to other pools
        new_other_pool = k / new_outcome_pool
        cost = other_pools_total - new_other_pool
        
        # Add slippage (0.5% fee)
        cost_with_fee = cost * 1.005
        
        return max(cost_with_fee, 0.01 * amount)  # Minimum 1% of shares value
    
    def calculate_sell_price(self, outcome: str, amount: float, pools: Dict[str, float]) -> float:
        """
        Calculate how much you receive for selling 'amount' of shares
        """
        if amount <= 0:
            return 0.0
        
        outcome_pool = pools[outcome]
        
        # Can't sell more than you have
        if amount > outcome_pool * 0.5:  # Limit to 50% of pool
            amount = outcome_pool * 0.5
        
        other_pools_total = sum(p for o, p in pools.items() if o != outcome)
        
        # Calculate payout
        k = outcome_pool * other_pools_total
        new_outcome_pool = outcome_pool - amount
        new_other_pool = k / new_outcome_pool if new_outcome_pool > 0 else 0
        payout = new_other_pool - other_pools_total
        
        # Subtract fee (0.5%)
        payout_with_fee = payout * 0.995
        
        return max(payout_with_fee, 0.0)
    
    def get_market_depth(self, outcome: str, pools: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate how much you can buy/sell at different price points
        Returns depth information for order book visualization
        """
        current_price = self.calculate_price(outcome, pools)
        
        # Calculate costs for different amounts
        amounts = [1, 5, 10, 25, 50, 100]
        depth = {
            'current_price': current_price,
            'buy_costs': {},
            'sell_payouts': {}
        }
        
        for amount in amounts:
            buy_cost = self.calculate_buy_price(outcome, amount, pools)
            sell_payout = self.calculate_sell_price(outcome, amount, pools)
            
            depth['buy_costs'][str(amount)] = {
                'cost': buy_cost,
                'avg_price': buy_cost / amount if amount > 0 else 0
            }
            depth['sell_payouts'][str(amount)] = {
                'payout': sell_payout,
                'avg_price': sell_payout / amount if amount > 0 else 0
            }
        
        return depth


def get_market_maker() -> MarketMaker:
    """Factory function to get a configured market maker instance"""
    return MarketMaker(initial_liquidity=1000.0)

