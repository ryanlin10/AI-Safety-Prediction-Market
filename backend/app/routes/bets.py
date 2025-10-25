from flask import Blueprint, request, jsonify
from app import db
from app.models import Bet, Market
from datetime import datetime

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

