from flask import Blueprint, request, jsonify
from app import db
from app.models import Bet, Market
from app.services.market_maker import get_market_maker
from datetime import datetime
import json

bp = Blueprint('bets', __name__, url_prefix='/api')

@bp.route('/markets/<int:market_id>/bets', methods=['GET'])
def get_market_bets(market_id):
    """Get all bets for a specific market"""
    market = Market.query.get_or_404(market_id)
    bets = market.bets.order_by(Bet.created_at.desc()).all()
    
    return jsonify({
        'market_id': market_id,
        'bets': [bet.to_dict() for bet in bets]
    }), 200

@bp.route('/markets/<int:market_id>/bets', methods=['POST'])
def place_bet(market_id):
    """Place a bet on a market"""
    market = Market.query.get_or_404(market_id)
    
    if market.status != 'active':
        return jsonify({'error': 'Market is not active'}), 400
    
    data = request.get_json()
    
    required_fields = ['outcome', 'stake', 'odds']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate outcome
    if data['outcome'] not in market.outcomes:
        return jsonify({'error': 'Invalid outcome'}), 400
    
    bet = Bet(
        market_id=market_id,
        user_id=data.get('user_id'),
        agent_id=data.get('agent_id'),
        outcome=data['outcome'],
        stake=data['stake'],
        odds=data['odds'],
        rationale=data.get('rationale')
    )
    
    db.session.add(bet)
    db.session.commit()
    
    return jsonify(bet.to_dict()), 201

@bp.route('/bets/<int:bet_id>', methods=['GET'])
def get_bet(bet_id):
    """Get a specific bet"""
    bet = Bet.query.get_or_404(bet_id)
    return jsonify(bet.to_dict()), 200

@bp.route('/markets/<int:market_id>/prices', methods=['GET'])
def get_market_prices(market_id):
    """Get current prices for all outcomes in a market"""
    market = Market.query.get_or_404(market_id)
    
    # Parse outcomes from JSON string
    try:
        outcomes = json.loads(market.outcomes) if isinstance(market.outcomes, str) else market.outcomes
    except:
        outcomes = market.outcomes
    
    # Get all bets for this market
    bets = market.bets.all()
    
    # Calculate prices using market maker
    mm = get_market_maker()
    pools = mm.get_liquidity_pools(outcomes, bets)
    prices = mm.calculate_all_prices(outcomes, bets)
    
    # Calculate buy/sell prices for a standard amount (10 shares)
    standard_amount = 10.0
    pricing_info = {}
    
    for outcome in outcomes:
        buy_cost = mm.calculate_buy_price(outcome, standard_amount, pools)
        sell_payout = mm.calculate_sell_price(outcome, standard_amount, pools)
        
        pricing_info[outcome] = {
            'current_price': prices[outcome],
            'buy_price': buy_cost / standard_amount,  # Price per share
            'sell_price': sell_payout / standard_amount if standard_amount > 0 else 0,
            'liquidity': pools[outcome]
        }
    
    return jsonify({
        'market_id': market_id,
        'prices': pricing_info,
        'total_volume': sum(bet.stake for bet in bets)
    }), 200

@bp.route('/markets/<int:market_id>/buy', methods=['POST'])
def buy_shares(market_id):
    """Buy contracts of an outcome (Kalshi-style)"""
    market = Market.query.get_or_404(market_id)
    
    if market.status != 'active':
        return jsonify({'error': 'Market is not active'}), 400
    
    data = request.get_json()
    
    if 'outcome' not in data or 'amount' not in data:
        return jsonify({'error': 'Missing outcome or amount'}), 400
    
    outcome = data['outcome']
    amount = float(data['amount'])  # Dollar amount to spend
    
    # Parse outcomes
    try:
        outcomes = json.loads(market.outcomes) if isinstance(market.outcomes, str) else market.outcomes
    except:
        outcomes = market.outcomes
    
    if outcome not in outcomes:
        return jsonify({'error': 'Invalid outcome'}), 400
    
    if amount <= 0:
        return jsonify({'error': 'Amount must be positive'}), 400
    
    # Get current market price for the outcome
    bets = market.bets.all()
    mm = get_market_maker()
    current_prices = mm.calculate_all_prices(outcomes, bets)
    current_price = current_prices.get(outcome, 0.5)  # Default to 50% if no price
    
    # In Kalshi-style markets:
    # - Each contract costs the current price (e.g., $0.65 for 65% probability)
    # - Each contract pays $1.00 if correct, $0.00 if wrong
    # - Number of contracts = amount spent / current price
    contracts = amount / current_price if current_price > 0 else 0
    
    if contracts <= 0:
        return jsonify({'error': 'Invalid number of contracts'}), 400
    
    # Potential payout if correct: contracts × $1.00
    potential_payout = contracts * 1.0
    # Potential profit if correct: payout - cost
    potential_profit = potential_payout - amount
    
    # Record the bet
    bet = Bet(
        market_id=market_id,
        user_id=data.get('user_id', 1),  # Default user for now
        outcome=outcome,
        stake=amount,  # Amount spent
        odds=current_price,  # Price at time of purchase
        rationale=f'Bought {contracts:.2f} contracts at ${current_price:.2f} each. Pays ${potential_payout:.2f} if {outcome}.'
    )
    
    db.session.add(bet)
    db.session.commit()
    
    # Return updated prices (prices update based on volume)
    new_bets = market.bets.all()
    new_prices = mm.calculate_all_prices(outcomes, new_bets)
    
    return jsonify({
        'success': True,
        'bet': bet.to_dict(),
        'amount_spent': amount,
        'contracts_purchased': round(contracts, 2),
        'purchase_price': round(current_price, 2),
        'potential_payout': round(potential_payout, 2),
        'potential_profit': round(potential_profit, 2),
        'new_prices': new_prices
    }), 201

@bp.route('/markets/<int:market_id>/price-history', methods=['GET'])
def get_price_history(market_id):
    """Get price history for all outcomes over time"""
    market = Market.query.get_or_404(market_id)
    
    # Parse outcomes
    try:
        outcomes = json.loads(market.outcomes) if isinstance(market.outcomes, str) else market.outcomes
    except:
        outcomes = market.outcomes
    
    # Get all bets ordered by time
    bets = market.bets.order_by(Bet.created_at).all()
    
    mm = get_market_maker()
    
    # Build price history by replaying bets
    history = []
    
    # Initial state (no bets)
    initial_pools = mm.get_liquidity_pools(outcomes, [])
    initial_prices = mm.calculate_all_prices(outcomes, [])
    history.append({
        'timestamp': market.created_at.isoformat(),
        'prices': initial_prices,
        'volume': 0
    })
    
    # Replay each bet
    cumulative_bets = []
    for bet in bets:
        cumulative_bets.append(bet)
        pools = mm.get_liquidity_pools(outcomes, cumulative_bets)
        prices = mm.calculate_all_prices(outcomes, cumulative_bets)
        
        history.append({
            'timestamp': bet.created_at.isoformat(),
            'prices': prices,
            'volume': sum(b.stake for b in cumulative_bets),
            'bet_id': bet.id,
            'outcome': bet.outcome
        })
    
    return jsonify({
        'market_id': market_id,
        'history': history
    }), 200

